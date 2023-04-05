# define the dictionaries of objects to be simulated and their parameters
from extraction.electrons import electrons 
from models.electrons.geneleeff import ElectronClassifier
from models.electrons.fromgenele import load_mixture_model
from postprocessing.electrons.columns_ele_old import ele_cond, reco_columns
from postprocessing.electrons.post_actions_ele_old import vars_dictionary


objs_dicts = {
    "Electron": {
    "derived_vars_func": electrons.extractGenElectronFeatures,
    "model": ElectronClassifier,
    "model_path":"~/FlashSim-Electrons/efficiencies/models/efficiency_electrons.pt",
    "flow_loader": load_mixture_model,
    "flow_path": "~/wipfs/generation/electrons/EM1/checkpoint-latest.pt",
    "gen_columns": ele_cond,
    "reco_columns": reco_columns,
    "vars_dictionary": vars_dictionary,
    "scale_file_path": "nbd/postprocessing/electrons/scale_factors_ele_old.json",
    "batch_size":10000,
    "saturate_ranges_path": "nbd/postprocessing/electrons/saturate_ranges_ele_old.json",
    "eff":True,
    }
}
