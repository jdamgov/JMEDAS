from ROOT import *
#from Analysis.JMEDAS.tdrstyle_mod14 import *
from tdrstyle_mod14 import *
from collections import OrderedDict
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--doPUPPI', action='store_true', default=False, dest='doPUPPI',
                  help='Plot the PFPuppi algorithm as well (if it exists in the ntuple')
parser.add_option('--drawFits', action='store_true', default=False, dest='drawFits',
                  help='Flag to draw, or not, the Gaussian fits to the response curves')
parser.add_option('--drawLines', action='store_false', default=True, dest='drawLines',
                  help='Flag to draw, or not, the lines at the mean of the Gaussian fit')
parser.add_option('--ifilename', type='string', action='store', default='pileupNtuple.root',
		  dest='ifilename', help='The name of the input ROOT file.')
parser.add_option('--algsize', type='string', action='store', default='AK4', dest='algsize',
		  help="The algorithm and size of the jet collections to get from the ntuple.")
parser.add_option('--maxEvents', type='int', action='store', default=-1, dest='maxEvents',
                  help="The maximum number of events in the tree to use (default=-1 is all events).")
(options, args) = parser.parse_args()

# Set the ROOT style
gROOT.Macro("rootlogon.C")
setTDRStyle()

#bmark = TBenchmark()
#bmark.Start("benchmark")

#Settings for each of the pads in the canvas
settingsTMP = {'response' : (1,0.75,1.25,0.0,0.225,"Response (p_{T}^{RECO}/p_{T}^{GEN})","a.u.",False),
			   'pt'       : (2,10.0,200.0,0.0,0.1,"p_{T}^{RECO}","a.u.",True),
			   'eta' 	  : (3,-2.5,2.5,0.0,0.15,"#eta","a.u.",False),
			   'phi' 	  : (4,-3.14159,3.14159,0.0,0.05,"#phi","a.u.",False)
			   }
settings = OrderedDict(sorted(settingsTMP.items(), key=lambda x:x[1], reverse=False))

# Create and draw the canvas
frames = []
for f, s in enumerate(settings) :
	frame = TH1D()
	frames.append(frame)
	frames[f].GetXaxis().SetLimits(settings[s][1],settings[s][2])
	frames[f].GetYaxis().SetRangeUser(settings[s][3],settings[s][4])
	frames[f].GetXaxis().SetTitle(settings[s][5])
	frames[f].GetYaxis().SetTitle(settings[s][6])
	if settings[s][6] :
		frames[f].GetXaxis().SetMoreLogLabels()
		frames[f].GetXaxis().SetNoExponent()
c = tdrCanvasMultipad("c",frames,14,11,2,2)

# Open the ROOT file with the ntuple
f = TFile(options.ifilename)

# Histogram settings
alg_size = options.algsize
jetTypes = OrderedDict([("PF" , kBlack),("PFCHS" , kRed),("PFPuppi" , kBlue)])
#corrections = OrderedDict([("Uncorrected" , kDashed),("L1" , kDotted),("L1L2L3" , kSolid)])
corrections = OrderedDict([("Uncorrected" , 7),("L1" , 5),("L1L2L3" , 1)])
hsettingsTMP = {'response' : (1,80,0,2),
		'pt'       : (2,200,0,1000),
	 	'eta' 	   : (3,50,-5,5),
		'phi' 	   : (4,50,-3.14159,3.14159),
	       }
hsettings = OrderedDict(sorted(hsettingsTMP.items(), key=lambda x:x[1], reverse=False))
nsigma = 1.0

histograms = {}
fits = {}
lines = {}
legends = {}
for hs in hsettings:
	print "Creating the",hs,"pad ... "
	for jt in jetTypes:
		for cor in corrections:	
			# Create the histograms
			hname = "h"+alg_size+jt+"_"+cor+"_"+hs

			print "\tCreating the histogram",hname,"..."

			histograms[hname] = TH1D(hname,hname,hsettingsTMP[hs][1],hsettingsTMP[hs][2],hsettingsTMP[hs][3])
			histograms[hname].SetLineWidth(2)

hsnames = hsettings.keys()
for jt in jetTypes:
	if not options.doPUPPI and jt == "PFPuppi":
		continue
#      	if not f.GetDirectory(alg_size+jt.upper()+"L1L2L3"):
	if not f.GetDirectory(alg_size+jt+"L1L2L3"):
	       	continue

#	tree = f.Get(alg_size+jt.upper()+"L1L2L3/t")
	tree = f.Get(alg_size+jt+"L1L2L3/t")
	print "\tRunning over ",alg_size+jt 
	# Fill the histograms
	for ievent, event in enumerate(tree):
		if options.maxEvents>-1 and ievent > options.maxEvents:
			continue
		for jet, pt_from_tree in enumerate(event.jtpt):
			pt_uncorrected = (pt_from_tree*event.jtjec[jet][0].second)
			pt_L1 = (pt_from_tree*event.jtjec[jet][1].second)
			pt_updated = pt_from_tree
			if event.refpt[jet]==0:
				continue
			for hs in hsnames:
				for cor in corrections:	
					hname = "h"+alg_size+jt+"_"+cor+"_"+hs
					rsp_uncorrected = pt_uncorrected/event.refpt[jet]
					rsp_L1 = pt_L1/event.refpt[jet]
					rsp_updated = pt_updated/event.refpt[jet]
					if rsp_updated<2.0 and rsp_updated>0.0 and abs(event.jteta[jet])<1.3 and event.refpt[jet] > 20. and cor=="L1L2L3":
					        #print "JEC Level: "+str(event.jtjec[jet][0].first)+"\tJEC Factor: "+str(event.jtjec[jet][0].second)+"\tOriginal pT: "+str(pt_from_tree)+"\tUncorrected pT: "+str(pt_from_tree/event.jtjec[jet][0].second)+"\tRef pT: "+str(event.refpt[jet])
					        #print "JEC Level: "+str(event.jtjec[jet][1].first)+"\tJEC Factor: "+str(event.jtjec[jet][1].second)+"\tOriginal pT: "+str(pt_from_tree)+"\tUncorrected pT: "+str(pt_from_tree/event.jtjec[jet][1].second)+"\tRef pT: "+str(event.refpt[jet])
						if hs == "response":
							histograms[hname].Fill(rsp_updated)
						elif hs == "pt":
							histograms[hname].Fill(pt_updated)
						elif hs == "eta":
							histograms[hname].Fill(event.jteta[jet])
						elif hs == "phi":
							histograms[hname].Fill(event.jtphi[jet])
					if rsp_L1<2.0 and rsp_L1>0.0 and abs(event.jteta[jet])<1.3 and event.refpt[jet] > 20. and cor=="L1":
						if hs == "response":
							histograms[hname].Fill(rsp_L1)
						elif hs == "pt":
							histograms[hname].Fill(pt_L1)
						elif hs == "eta":
							histograms[hname].Fill(event.jteta[jet])
						elif hs == "phi":
							histograms[hname].Fill(event.jtphi[jet])
					if rsp_uncorrected<2.0 and rsp_uncorrected>0.0 and abs(event.jteta[jet])<1.3 and event.refpt[jet] > 20. and cor=="Uncorrected":
						if hs == "response":
							histograms[hname].Fill(rsp_uncorrected)
						elif hs == "pt":
							histograms[hname].Fill(pt_uncorrected)
						elif hs == "eta":
							histograms[hname].Fill(event.jteta[jet])
						elif hs == "phi":
							histograms[hname].Fill(event.jtphi[jet])

for hs in hsnames:
	legname = "leg_"+hs
	legends[legname] = tdrLeg(0.65,0.65,0.8,0.9)
	legends[legname].SetTextSize(0.0325)
	legends[legname].SetTextFont(42)
	legnumber = "legnum_"+hs
	legends[legnumber] = tdrLeg(0.375,0.65,0.525,0.9)
	legends[legnumber].SetTextSize(0.0325)
	legends[legnumber].SetTextFont(42)

	for jt in jetTypes:
		for icor,cor in enumerate(corrections):	
			hname = "h"+alg_size+jt+"_"+cor+"_"+hs
			icol = jetTypes[jt]
			if icor == 0:
 				icol = max(jetTypes[jt]-6,15)
			if icor == 1:
 				icol = max(jetTypes[jt]+2,28)
			if icor == 2:
 				icol = jetTypes[jt]
  			if histograms[hname].Integral()==0:
				continue
			#print hname,histograms[hname].Integral()
			# Normalize the histograms
			histograms[hname].Scale(1.0/histograms[hname].Integral())

			if hs == "response":
				# Fit a Gaussian to the response curves
				fname = "f"+alg_size+jt+"_"+cor+"_"+hs
				fits[fname] = TF1(fname,"gaus",histograms[hname].GetMean()-(nsigma*histograms[hname].GetRMS()),histograms[hname].GetMean()+(nsigma*histograms[hname].GetRMS()))
				fits[fname].SetParNames("N","#mu","#sigma")
				#fits[fname].SetLineColor(jetTypes[jt])
				fits[fname].SetLineColor(icol)
				fits[fname].SetLineStyle(corrections[cor])
				histograms[hname].Fit(fits[fname],"RQ0")
				numberstring = "res "+str(round(fits[fname].GetParameter(1),2))+"#pm"+str(round(fits[fname].GetParameter(2),2))
				legends[legnumber].AddEntry(histograms[hname],numberstring,"l")

				# Create lines based on the fits
				lname = "l"+alg_size+jt+"_"+cor+"_"+hs
				lines[lname] = TArrow(fits[fname].GetParameter(1),settings["response"][3],fits[fname].GetParameter(1),settings["response"][4]/4.,0.02,"<|")
				lines[lname].SetAngle(40);
				#lines[lname].SetLineColor(jetTypes[jt])
				lines[lname].SetLineColor(icol)
				lines[lname].SetFillColor(icol)
				lines[lname].SetLineStyle(corrections[cor])

			# Add entries to the legend		
			legends[legname].AddEntry(histograms[hname],str(alg_size+jt+cor).replace("Uncorrected",""),"l")

			c.cd(hsettingsTMP[hs][0])
			#tdrDraw(histograms[hname],"HIST",kNone,jetTypes[jt],corrections[cor],-1,0,0)
			tdrDraw(histograms[hname],"HIST",kNone,icol,corrections[cor],-1,0,0)

			if hs == "response":
				#print hname,histograms[hname].GetMean(),histograms[hname].GetRMS(),"fit",fits[fname].GetParameter(1),fits[fname].GetParameter(2)
				# Draw the fits
				if options.drawFits:
					c.cd(hsettingsTMP[hs][0])
					fits[fname].Draw("same")

				# Draw the lines
				if options.drawLines:
					c.cd(hsettingsTMP[hs][0])
					#lines[lname].Draw("same")
					lines[lname].Draw("")
			elif hs == "pt":
				gPad.SetLogx()

	#Draw the legend
	c.cd(hsettingsTMP[hs][0])
	legends[legname].Draw("same")
	if hs == "response":
		legends[legnumber].Draw("same")
c.Update()
c.Draw()


# Save the canvases
c.Print('plots_pileup_2.png', 'png')

#bmark.Stop("benchmark")
#print 'CPU  time: ',bmark.GetCpuTime("benchmark")
#print 'real time: ',bmark.GetRealTime("benchmark")
