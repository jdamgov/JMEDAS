from ROOT import *
from collections import OrderedDict
from Analysis.JMEDAS.tdrstyle_mod14 import *
from math import *

# Set the ROOT style
gROOT.Macro("rootlogon.C")
setTDRStyle()

file = TFile("pileupNtuple_DY.root", "READ")
# Large ntuples for DYjets and QCD are available
#file = TFile.Open("root://cmseos.fnal.gov//store/user/cmsdas/2016/SHORT_EXERCISES/PileupAndMET/pileupNtuple_QCD.root","READ")
#file = TFile.Open("root://cmseos.fnal.gov//store/user/cmsdas/2016/SHORT_EXERCISES/PileupAndMET/pileupNtuple_DYjets.root","READ")

tree = file.Get("AK4PFPuppiL1L2L3/t")
entries = tree.GetEntriesFast()

metHist = TH1F("met", "met;MET [GeV];Events", 50, 0, 200)
ptHist = TH1F("pt", "pt;Muon p_{T} [GeV];Muons", 50, 0, 200)
etaHist = TH1F("eta", "etat;Muon Eta [GeV];Muons", 50, -3, 3)
phiHist = TH1F("phi", "phi;Muon Phi [GeV];Muons", 50, -4, 4)
massHist = TH1F("mass", "mass;Dimuon Mass [GeV];Events", 50, 0, 200)
uperpHist = TH1F("uPerp", "uPerp;Perpendicular Recoil [GeV];Events", 50, -100, 100)
uparlHist = TH1F("uParl", "uParl;Parallel Recoil [GeV];Events", 50, -100, 100)

metPUPPIHist = TH1F("metPUPPI", "metPUPPI;MET [GeV];Events", 50, 0, 200)
uperpPUPPIHist = TH1F("uPerpPUPPI", "uPerpPUPPI;Perpendicular Recoil [GeV];Events", 50, -100, 100)
uparlPUPPIHist = TH1F("uParlPUPPI", "uParl;Parallel Recoil [GeV];Events", 50, -100, 100)


for entry in xrange(entries):

	ientry = tree.LoadTree( entry )
	if ientry < 0:
		break

	nb = tree.GetEntry( ientry )
	if nb <= 0:
		continue

	if len(tree.mupt) < 2:
		continue

	mu1pt = tree.mupt[0]
	mu2pt = tree.mupt[1]

	mu1phi = tree.muphi[0]
	mu2phi = tree.muphi[1]

	mu1eta = tree.mueta[0]
	mu2eta = tree.mueta[1]


	if (not(mu1pt > 20.0 and mu2pt > 20.0)):
		continue	

	ptHist.Fill(tree.mue[0])
	ptHist.Fill(tree.mue[1])

	etaHist.Fill(mu1eta)
	etaHist.Fill(mu2eta)

	phiHist.Fill(mu1phi)
	phiHist.Fill(mu2phi)	






	mu1V = TLorentzVector()
	mu1V.SetPtEtaPhiE(tree.mupt[0], mu1eta, mu1phi, tree.mue[0])
	mu2V = TLorentzVector()
	mu2V.SetPtEtaPhiE(tree.mupt[1], mu2eta, mu2phi, tree.mue[1])




	dyV = TLorentzVector()
	dyV = mu1V + mu2V


	massHist.Fill(dyV.M() )

	metV = TLorentzVector()
	metPUPPIV = TLorentzVector()
	
	metV.SetPtEtaPhiM( tree.metpt[0], tree.meteta[0], tree.metphi[0], tree.metpt[0])
	metPUPPIV.SetPtEtaPhiM( tree.metPUPPIpt[0], tree.metPUPPIeta[0], tree.metPUPPIphi[0], tree.metPUPPIpt[0])



	metpt = tree.metpt[0]
	metPUPPIpt = tree.metPUPPIpt[0]
	dimupt = dyV.Pt()

	metHist.Fill( metpt )
	metPUPPIHist.Fill( metPUPPIpt )
	

        dyV.SetPz(0.)
	met3V = (metV).Vect()	
	metPUPPI3V = (metPUPPIV).Vect()	
	dy3V = dyV.Vect()

	uparl = met3V.Dot(dy3V) / (dy3V.Mag())
	uparl3V = uparl*met3V.Unit()
	uperp3V = met3V - uparl3V
	uperp = met3V.Dot(dy3V.Orthogonal()) / (dy3V.Mag())
	#print uparl, uperp

	uparlPUPPI = metPUPPI3V.Dot(dy3V) / (dy3V.Mag())
	uparlPUPPI3V = uparlPUPPI*metPUPPI3V.Unit()
	uperpPUPPI3V = metPUPPI3V - uparlPUPPI3V
	uperpPUPPI = metPUPPI3V.Dot(dy3V.Orthogonal()) / (dy3V.Mag())


	if (dimupt > 0.0):
		uperpHist.Fill( uperp )
		uparlHist.Fill( uparl )
		uperpPUPPIHist.Fill( uperpPUPPI )
		uparlPUPPIHist.Fill( uparlPUPPI )


leg = TLegend(0.7, 0.7, 0.94, 0.94)
leg.SetLineColor(0)
leg.SetFillColor(0)
leg.AddEntry(metPUPPIHist, "PUPPI MET", "l")
leg.AddEntry(metHist, "PF MET", "l")



c1 = TCanvas()
c1.cd()
metPUPPIHist.SetLineColor(kRed)
metPUPPIHist.Draw()
metHist.Draw("same")
leg.Draw("same")
c2 = TCanvas()
c2.cd()
uperpPUPPIHist.SetLineColor(kRed)
uperpPUPPIHist.Draw()
uperpHist.Draw("same")
leg.Draw("same")
c3 = TCanvas()
c3.cd()
uparlPUPPIHist.SetLineColor(kRed)
uparlPUPPIHist.Draw()
uparlHist.Draw("same")
leg.Draw("same")

c4 = TCanvas()
massHist.Draw()

