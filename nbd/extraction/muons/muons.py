import os
import ROOT

module_path = os.path.join(os.path.dirname(__file__), "muons.h")

ROOT.gInterpreter.ProcessLine(f'#include "{module_path}"')

def jet_cleaning(d):
    cleaned = (
        d.Define("TMPGenElectronMask", "abs(GenPart_pdgId) == 11")
        .Define("TMPGenElectron_pt", "GenPart_pt[TMPGenElectronMask]")
        .Define("TMPGenElectron_eta", "GenPart_eta[TMPGenElectronMask]")
        .Define("TMPGenElectron_phi", "GenPart_phi[TMPGenElectronMask]")
        .Define("TMPGenMuonMask", "abs(GenPart_pdgId) == 13")
        .Define("TMPGenMuon_pt", "GenPart_pt[TMPGenMuonMask]")
        .Define("TMPGenMuon_eta", "GenPart_eta[TMPGenMuonMask]")
        .Define("TMPGenMuon_phi", "GenPart_phi[TMPGenMuonMask]")
        .Define(
            "CleanGenJet_mask_ele",
            "clean_genjet_mask(GenJet_pt, GenJet_eta, GenJet_phi, TMPGenElectron_pt, TMPGenElectron_eta, TMPGenElectron_phi)",
        )
        .Define(
            "CleanGenJet_mask_muon",
            "clean_genjet_mask(GenJet_pt, GenJet_eta, GenJet_phi, TMPGenMuon_pt, TMPGenMuon_eta, TMPGenMuon_phi)",
        )
        .Define("CleanGenJetMask", "CleanGenJet_mask_ele && CleanGenJet_mask_muon")
        .Define("CleanGenJet_pt", "GenJet_pt[CleanGenJetMask]")
        .Define("CleanGenJet_eta", "GenJet_eta[CleanGenJetMask]")
        .Define("CleanGenJet_phi", "GenJet_phi[CleanGenJetMask]")
        .Define("CleanGenJet_mass", "GenJet_mass[CleanGenJetMask]")
        .Define(
            "CleanGenJet_hadronFlavour_uchar", "GenJet_hadronFlavour[CleanGenJetMask]"
        )
        .Define(
            "CleanGenJet_hadronFlavour",
            "static_cast<ROOT::VecOps::RVec<int>>(CleanGenJet_hadronFlavour_uchar)",
        )
        .Define("CleanGenJet_partonFlavour", "GenJet_partonFlavour[CleanGenJetMask]")
    )

    return cleaned

def extractGenMuonFeatures(df):
    """for going from GenJet to reco jet

    Args:
        df (rdataframe): original rdataframe (cleaned from genpart into genjet)

    Returns:
        rdataframe: rdataframe with new features
    """
    df1 = jet_cleaning(df)
    extracted = (
        df1.Define(
            "MuonMaskJ",
            "(GenPart_pdgId == 13 | GenPart_pdgId == -13)&&((GenPart_statusFlags & 8192) > 0)",
        )
        .Define("MGenMuon_eta", "GenPart_eta[MuonMaskJ]")
        .Define("MGenMuon_pdgId", "GenPart_pdgId[MuonMaskJ]")
        .Define("MGenMuon_charge", "Mcharge(MGenMuon_pdgId)")
        .Define("MGenMuon_phi", "GenPart_phi[MuonMaskJ]")
        .Define("MGenMuon_pt", "GenPart_pt[MuonMaskJ]")
        .Define("MGenPart_statusFlags", "GenPart_statusFlags[MuonMaskJ]")
        .Define("MGenPart_statusFlags0", "MBitwiseDecoder(MGenPart_statusFlags, 0)")
        .Define("MGenPart_statusFlags1", "MBitwiseDecoder(MGenPart_statusFlags, 1)")
        .Define("MGenPart_statusFlags2", "MBitwiseDecoder(MGenPart_statusFlags, 2)")
        .Define("MGenPart_statusFlags3", "MBitwiseDecoder(MGenPart_statusFlags, 3)")
        .Define("MGenPart_statusFlags4", "MBitwiseDecoder(MGenPart_statusFlags, 4)")
        .Define("MGenPart_statusFlags5", "MBitwiseDecoder(MGenPart_statusFlags, 5)")
        .Define("MGenPart_statusFlags6", "MBitwiseDecoder(MGenPart_statusFlags, 6)")
        .Define("MGenPart_statusFlags7", "MBitwiseDecoder(MGenPart_statusFlags, 7)")
        .Define("MGenPart_statusFlags8", "MBitwiseDecoder(MGenPart_statusFlags, 8)")
        .Define("MGenPart_statusFlags9", "MBitwiseDecoder(MGenPart_statusFlags, 9)")
        .Define("MGenPart_statusFlags10", "MBitwiseDecoder(MGenPart_statusFlags, 10)")
        .Define("MGenPart_statusFlags11", "MBitwiseDecoder(MGenPart_statusFlags, 11)")
        .Define("MGenPart_statusFlags12", "MBitwiseDecoder(MGenPart_statusFlags, 12)")
        .Define("MGenPart_statusFlags13", "MBitwiseDecoder(MGenPart_statusFlags, 13)")
        .Define("MGenPart_statusFlags14", "MBitwiseDecoder(MGenPart_statusFlags, 14)")
        .Define(
            "ClosestJet_dr",
            "Mclosest_jet_dr(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi)",
        )
        .Define(
            "ClosestJet_deta",
            "Mclosest_jet_deta(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi)",
        )
        .Define(
            "ClosestJet_dphi",
            "Mclosest_jet_dphi(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi)",
        )
        .Define(
            "ClosestJet_pt",
            "Mclosest_jet_pt(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_pt)",
        )
        .Define(
            "ClosestJet_mass",
            "Mclosest_jet_mass(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_mass)",
        )
        .Define(
            "ClosestJet_EncodedPartonFlavour_light",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_partonFlavour, ROOT::VecOps::RVec<int>{1,2,3})",
        )
        .Define(
            "ClosestJet_EncodedPartonFlavour_gluon",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_partonFlavour, ROOT::VecOps::RVec<int>{21})",
        )
        .Define(
            "ClosestJet_EncodedPartonFlavour_c",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_partonFlavour, ROOT::VecOps::RVec<int>{4})",
        )
        .Define(
            "ClosestJet_EncodedPartonFlavour_b",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_partonFlavour, ROOT::VecOps::RVec<int>{5})",
        )
        .Define(
            "ClosestJet_EncodedPartonFlavour_undefined",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_partonFlavour, ROOT::VecOps::RVec<int>{0})",
        )
        .Define(
            "ClosestJet_EncodedHadronFlavour_b",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_hadronFlavour, ROOT::VecOps::RVec<int>{5})",
        )
        .Define(
            "ClosestJet_EncodedHadronFlavour_c",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_hadronFlavour, ROOT::VecOps::RVec<int>{4})",
        )
        .Define(
            "ClosestJet_EncodedHadronFlavour_light",
            "closest_jet_flavour_encoder(CleanGenJet_eta, CleanGenJet_phi, MGenMuon_eta, MGenMuon_phi, CleanGenJet_hadronFlavour, ROOT::VecOps::RVec<int>{0})",
        )
        .Define("MMuon_charge", "Muon_charge[MuonMask]")
        .Define("MMuon_cleanmask", "Muon_cleanmask[MuonMask]")
        .Define("MMuon_dxy", "Muon_dxy[MuonMask]")
        .Define("MMuon_dxyErr", "Muon_dxyErr[MuonMask]")
        .Define("MMuon_dxybs", "Muon_dxybs[MuonMask]")
        .Define("MMuon_dz", "Muon_dz[MuonMask]")
        .Define("MMuon_dzErr", "Muon_dzErr[MuonMask]")
        .Define("MMuon_etaMinusGen", "Muon_eta[MuonMask]-MGenMuon_eta")
        .Define("MMuon_highPtId", "Muon_highPtId[MuonMask]")
        .Define("MMuon_highPurity", "Muon_highPurity[MuonMask]")
        .Define("MMuon_inTimeMuon", "Muon_inTimeMuon[MuonMask]")
        .Define("MMuon_ip3d", "Muon_ip3d[MuonMask]")
        .Define("MMuon_isGlobal", "Muon_isGlobal[MuonMask]")
        .Define("MMuon_isPFcand", "Muon_isPFcand[MuonMask]")
        .Define("MMuon_isStandalone", "Muon_isStandalone[MuonMask]")
        .Define("MMuon_isTracker", "Muon_isTracker[MuonMask]")
        .Define("MMuon_jetPtRelv2", "Muon_jetPtRelv2[MuonMask]")
        .Define("MMuon_jetRelIso", "Muon_jetRelIso[MuonMask]")
        .Define("MMuon_looseId", "Muon_looseId[MuonMask]")
        .Define("MMuon_mediumId", "Muon_mediumId[MuonMask]")
        .Define("MMuon_mediumPromptId", "Muon_mediumPromptId[MuonMask]")
        .Define("MMuon_miniIsoId", "Muon_miniIsoId[MuonMask]")
        .Define("MMuon_miniPFRelIso_all", "Muon_miniPFRelIso_all[MuonMask]")
        .Define("MMuon_miniPFRelIso_chg", "Muon_miniPFRelIso_chg[MuonMask]")
        .Define("MMuon_multiIsoId", "Muon_multiIsoId[MuonMask]")
        .Define("MMuon_mvaId", "Muon_mvaId[MuonMask]")
        .Define("MMuon_mvaLowPt", "Muon_mvaLowPt[MuonMask]")
        .Define("MMuon_mvaLowPtId", "Muon_mvaLowPtId[MuonMask]")
        .Define("MMuon_mvaTTH", "Muon_mvaTTH[MuonMask]")
        .Define("MMuon_nStations", "Muon_nStations[MuonMask]")
        .Define("MMuon_nTrackerLayers", "Muon_nTrackerLayers[MuonMask]")
        .Define("MMuon_pfIsoId", "Muon_pfIsoId[MuonMask]")
        .Define("MMuon_pfRelIso03_all", "Muon_pfRelIso03_all[MuonMask]")
        .Define("MMuon_pfRelIso03_chg", "Muon_pfRelIso03_chg[MuonMask]")
        .Define("MMuon_pfRelIso04_all", "Muon_pfRelIso04_all[MuonMask]")
        .Define("MMuon_filteredphi", "Muon_phi[MuonMask]")
        .Define("MMuon_phiMinusGen", "DeltaPhi(MMuon_filteredphi, MGenMuon_phi)")
        .Define("MMuon_ptRatio", "Muon_pt[MuonMask]/MGenMuon_pt")
        .Define("MMuon_ptErr", "Muon_ptErr[MuonMask]")
        .Define("MMuon_puppiIsoId", "Muon_puppiIsoId[MuonMask]")
        .Define("MMuon_segmentComp", "Muon_segmentComp[MuonMask]")
        .Define("MMuon_sip3d", "Muon_sip3d[MuonMask]")
        .Define("MMuon_softId", "Muon_softId[MuonMask]")
        .Define("MMuon_softMva", "Muon_softMva[MuonMask]")
        .Define("MMuon_softMvaId", "Muon_softMvaId[MuonMask]")
        .Define("MMuon_tightCharge", "Muon_tightCharge[MuonMask]")
        .Define("MMuon_tightId", "Muon_tightId[MuonMask]")
        .Define("MMuon_tkIsoId", "Muon_tkIsoId[MuonMask]")
        .Define("MMuon_tkRelIso", "Muon_tkRelIso[MuonMask]")
        .Define("MMuon_triggerIdLoose", "Muon_triggerIdLoose[MuonMask]")
    )

    return extracted
