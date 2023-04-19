import os
import time
import numpy as np
import ROOT
import uproot
import awkward as ak
import pandas as pd
import torch
from torch.utils.data import DataLoader
import nbd.builder.core as core


def simulator(
    rdf,
    derived_vars_func,
    eff_model,
    eff_model_path,
    flow_loader,
    flow_path,
    eff_columns,
    gen_columns,
    reco_columns,
    vars_dictionary,
    scale_file_path,
    device="cpu",
    batch_size=10000,
    saturate_ranges_path=None,
    eff=True,
):
    # extract
    rdf_ass = derived_vars_func(rdf)
    if eff == True:
        a_gen_data = ak.from_rdataframe(
            rdf_ass, columns=eff_columns + gen_columns
        )  # no duplicate fields awkward 2.0
        if eff_model is not None:
            eff_model_init = eff_model(len(eff_columns))
        else:
            raise ValueError("Efficiency model path should be declared")
    else:
        a_gen_data = ak.from_rdataframe(rdf_ass, columns=gen_columns)
        eff_model_init = None
    to_flash, reco_struct = core.select_gen(
        a_gen_data,
        eff_columns,
        gen_columns,
        eff_model_init,
        eff_model_path,
        device=device,
        eff=eff,
        batch_size=batch_size,
    )

    a_flash = core.flash_simulate(
        flow_loader,
        flow_path,
        to_flash,
        gen_columns,
        reco_columns,
        vars_dictionary,
        scale_file_path,
        reco_struct,
        device=device,
        batch_size=10000,
        saturate_ranges_path=saturate_ranges_path,
    )
    # temporary fix to change charges
    if "MElectron_hoe" in reco_columns:
        charges = ak.unflatten(to_flash.GenElectron_charge, reco_struct)
        a_flash["MElectron_charge"] = charges

    return a_flash
