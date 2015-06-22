import os,pymongo,sys,itertools,cPickle as pickle

path = "/Users/kazjon/Dropbox/Documents/Research/UNCC/ComputationalCreativity/Datasets/BWReplays/mleece/SimplifiedByRace"

outfile = "parsed_games_noresearch_noupgrades_lim101"
dir1 = "Protoss"
dir2 = "Terran"
ext = ".atoms"
ignore = ["Move","Attack","AttackMove", "Research", "Upgrade"]
steplimit = 101 # Use 0 for no limit

repstreams = []
symbols = {}
actions = {}
	
def symbolise(act):
	if act in symbols.keys():
		return symbols[act]
	s = len(symbols.keys())
	print "New Symbol: (#"+str(s)+")",act
	symbols[act] = s
	actions[s] = act
	return s

for repfile in os.listdir(os.path.join(path,dir1)):
	repstream = [(0,symbolise("START()"))]
	#repstream = []
	fullpath1 = os.path.join(path,dir1,repfile)
	if os.path.isfile(fullpath1) and os.path.splitext(repfile)[-1] == ext:
		print repfile
		fullpath2 = os.path.join(path,dir2,repfile)
		if os.path.exists(fullpath2):
			with open(fullpath1,"rb") as rep1:
				rep1_lines = rep1.readlines()
			with open(fullpath2,"rb") as rep2:
				rep2_lines = rep2.readlines()
			it2 = iter(rep2_lines)
			it2done = False
			try:
				t2,act2 = it2.next().split()
			except StopIteration:
				it2done = True
			for l1 in rep1_lines:
				t1,act1 = l1.split()
				if not any([ig in act1 for ig in ignore]):
					while not it2done and int(t2) < int(t1):
						if not any([ig in act2 for ig in ignore]):
							act2 = "Opp_" + act2
							repstream.append((int(t2),symbolise(act2)))
						try:
							t2,act2 = it2.next().split()
						except StopIteration:
							it2done = True
					repstream.append((int(t1),symbolise(act1)))
			if steplimit:
				if len(repstream) > steplimit:
					repstream = repstream[0:steplimit]
				else:
					repstream = repstream + ([(repstream[-1][0],symbolise("GAMEOVER()"))] * (steplimit - len(repstream)))
			else:
				repstream.append((repstream[-1][0],symbolise("GAMEOVER()")))
				
			repstreams.append(repstream)
			print "  --",len(repstream)
			#print zip(*repstream)[1]
		else:
			print "  -- skipped as no matching file found."
print "Total reps:",len(repstreams)
repstreams_cat = list(itertools.chain.from_iterable(repstreams))
print "Total chars:",len(repstreams_cat)
print "Total symbols:",len(symbols.keys())
print symbols
print actions


with open(outfile+".pkl","wb") as f:
	pickle.dump({"streams":repstreams_cat,"symbols":symbols,"actions":actions},f)