import os
import time
import numpy as np
import ROOT
import uproot
import awkward as ak
import pandas as pd
import torch
from torch.utils.data import DataLoader
import nbd.builder.object_simulator as object_simulator
from nbd.builder.objs_dicts import objs_dicts
from nbd.utils.reco_full import get_reco_columns


def nanomaker(input_file, output_file, objects_keys=None, device="cpu", limit=None):
    print(f"Processing file {input_file}")

    file = ROOT.TFile.Open(input_file)
    events = file.Events
    lumi = file.LuminosityBlocks
    runs = file.Runs
    meta = file.MetaData

    if limit is not None:
        full = ROOT.RDataFrame(events).Range(limit)
    else:
        full = ROOT.RDataFrame(events)

    # Getting the list of columns
    full_columns_list = full.GetColumnNames()

    full_columns = []
    for name in full_columns_list:
        full_columns.append(str(name))

    # Selecting FullSim reco variables to copy in the FullSim tree
    # Reco objects are defined in reco_full.py

    old_reco_columns = get_reco_columns(full_columns)

    # Selecting the other variables

    remaining_columns = [var for var in full_columns if var not in old_reco_columns]

    a_rest = ak.from_rdataframe(full, columns=remaining_columns)
    # Flash simulation

    flash_list = []
    for obj in objects_keys:
        print(f"Simulating {obj} collection")
        a_flash = object_simulator.simulator(full, device=device, **objs_dicts[obj])
        print(f"Done")
        flash_list.append(a_flash)

    # explicit check on dict keys
    # merge same type of reco on the evet with ak.concatenate (for flash)
    dict_1 = dict(zip(a_rest.fields, [a_rest[field] for field in a_rest.fields]))
    for i in range(len(objects_keys)):
        dict_2 = dict(
            zip(
                flash_list[i].fields,  # TODO check if fields are the same
                [flash_list[i][field] for field in flash_list[i].fields],
            )
        )
        total = {**dict_1, **dict_2}
        dict_1 = total


    to_file = ak.to_rdataframe(total)
    to_file.Snapshot("Events", output_file)

    # add a new ttrees to the output file
    a_full = ak.from_rdataframe(full, columns=old_reco_columns)
    d_full = dict(zip(a_full.fields, [a_full[field] for field in a_full.fields]))
    old_reco = ak.to_rdataframe(d_full)

    opts = ROOT.RDF.RSnapshotOptions()
    opts.fMode = "Update"
    old_reco.Snapshot("FullSim", output_file, "", opts)

    outfile = ROOT.TFile.Open(output_file, "UPDATE")
    outfile.cd()
    lumi.Write()
    runs.Write()
    meta.Write()
    outfile.Close()

