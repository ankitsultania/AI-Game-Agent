import sys
import os
import string
import collections
import time

###############################################################
###################### GLOBALS ################################
inputfile = sys.argv[-1]
algo = 0
player = ""
cutoff = 0
#actual board values are from 1 to 25 in the list
boardvalue = [0]
#actual game state are from 1 to 25 in the list
gamestate = ['']#[["*" for x in range(5)] for x in range(5)]
player_conquered = []
opponent_conquered = []
unoccupied_sq = []
labeldict = {1:"A1", 6:"A2", 11:"A3", 16:"A4", 21:"A5", 2:"B1", 7:"B2", 12:"B3", 17:"B4", 22:"B5",
			 3:"C1", 8:"C2", 13:"C3", 18:"C4", 23:"C5", 4:"D1", 9:"D2", 14:"D3", 19:"D4", 24:"D5",
			 5:"E1", 10:"E2", 15:"E3", 20:"E4", 25:"E5", 0:"root"}
count = 0
###############################################################

#################### NODE CLASS ###############################
class Node:
	cavailable_moves = []
	cplayer =''
	copponent = ''
	cpcaptured = []
	cocaptured = []
	craidmoves = [] #computed for who is playing 
	csneakmoves = []
	cscore = 0
	clast_captured_sq = 0
	cnode_depth = 0
	alpha = float('-inf')
	beta = float('inf')
	
	def __init__(self, amoves, score, last_capture_sq, ndepth, p_cap, o_cap, p, o, alpha=float('-inf'), beta=float('inf')):
		self.cavailable_moves = amoves #its a list
		self.cscore = score
		self.clast_captured_sq = last_capture_sq
		self.cdepth = ndepth
		self.cpcaptured = p_cap
		self.cocaptured = o_cap
		self.cplayer = p
		self.copponent = o
		self.craidmoves = self.SetRaidmovesForPrevPlayer()#self.SetRaidmovesForCurrPlayer()
		self.csneakmoves = self.SetSneakmovesForPrevPlayer() #self.SetSneakmovesForCurrPlayer()
		self.alpha = alpha
		self.beta = beta
		
	def GetDepth(self):
		return self.cdepth
	def GetAvailableMoves(self):
		return self.cavailable_moves
	def GetLastCapturedSquare(self):
		return self.clast_captured_sq
	def GetBestScoreOnNode(self):
		return self.cscore
	def GetNextState(self, move):
		list1 = list(set(self.cavailable_moves) - set([move]))
		return list1
	def UpdateScore(self, x):
		self.cscore = x
	def UpdateMove(self, lastMove):
		self.clast_captured_sq = lastMove
	def SetRaidmovesForCurrPlayer(self):
			raid = []
			for sq in self.cpcaptured:
				if sq-5 >= 1: #up
					if sq-5 not in raid and sq-5 in self.cavailable_moves:
						riad.append(sq-5)
				if sq+5 <=25: #down
					if sq+5 not in raid and sq+5 in self.cavailable_moves:
						raid.append(sq+5)
		
				if sq-1%5 != 0: #left
					if sq-1 not in raid and sq-1 in self.cavailable_moves:
						raid.append(sq-1)
		
				if sq%5 !=0: #right
					if sq+1 not in raid and sq+1 in self.cavailable_moves:
						raid.append(sq+1)
			return raid
	def SetSneakmovesForCurrPlayer(self):
		list_temp = list(set(self.cavailable_moves) - set(self.craidmoves))
		return list_temp
	def SetRaidmovesForPrevPlayer(self):
			raid = []
			captured_exceptlast = list(set(self.cocaptured) - set([self.clast_captured_sq]))
			temp_available = self.cavailable_moves + [self.clast_captured_sq]
			for sq in captured_exceptlast:
				if sq-5 >= 1: #up
					if sq-5 not in raid and sq-5 in temp_available:
						raid.append(sq-5)
				if sq+5 <=25: #down
					if sq+5 not in raid and sq+5 in temp_available:
						raid.append(sq+5)
		
				if (sq-1)%5 != 0: #left
					if sq-1 not in raid and sq-1 in temp_available:
						raid.append(sq-1)
		
				if sq%5 !=0: #right
					if sq+1 not in raid and sq+1 in temp_available:
						raid.append(sq+1)
			return raid
	def SetSneakmovesForPrevPlayer(self):
		list_temp = list(set(self.cavailable_moves) - set(self.craidmoves))
		if self.clast_captured_sq not in self.craidmoves:
			new_list = list_temp + [self.clast_captured_sq]
		else:
			new_list = list_temp
		return new_list
	def UpdateConqueredSetOnRaid(self, toconvert):
		self.cpcaptured += toconvert
		self.cocaptured = list(set(self.cocaptured) - set(toconvert))
	def UpdateAlpha(self,x):
		self.alpha = x
	def UpdateBeta(self,x):
		self.beta = x
	def GetAlpha(self):
		return self.alpha
	def GetBeta(self):
		return self.beta
		
###############################################################

def OpenInputFile(path):
		fp = open(path, "r")
		return fp

def ReadCurrentGameState(file):
	#in total 13 lines
	global algo, player, cutoff, boardvalue
	for i, line in enumerate(file):
		if i == 0:
			algo = int(line)
		elif i == 1:
			player = line.rstrip()
		elif i == 2:
			cutoff = int(line)
		elif 3<= i <= 7:
			values = line.split(" ")
			for x in values:
				boardvalue.append(int(x))
		elif 8<= i <= 12:
			str = line.rstrip()
			for c in range(0,len(str)):
				gamestate.append(str[c])

def ReadGame(file):
	global p1, p1_algo, p1_cutoff, p2, p2_algo, p2_cutoff, gamestate, boardvalue
	for i, line in enumerate(file):
		if i == 1:
			p1 = line.rstrip()
		elif i == 2:
			p1_algo = int(line)
		elif i == 3:
			p1_cutoff = int(line)
		elif i == 4:
			p2 = line.rstrip()
		elif i == 5:
			p2_algo = int(line)
		elif i == 6:
			p2_cutoff = int(line)
		elif 7<= i <= 11:
			values = line.split(" ")
			for x in values:
				boardvalue.append(int(x))
		elif 12<= i <= 16:
			str = line.rstrip()
			for c in range(0,len(str)):
				gamestate.append(str[c])
	
def UpdateConqueredSquares(gamestate, player, opponent):
	for i in range(1,len(gamestate)):
		if gamestate[i] == player:
			player_conquered.append(i)
		elif gamestate[i] == opponent:
			opponent_conquered.append(i)
		else:
			unoccupied_sq.append(i)	
	return player_conquered, opponent_conquered, unoccupied_sq

def UpdateConqueredSquaresSimul(gamestate, player, opponent):
	play_conq, oppo_conq, un_conq = [], [], []
	for i in range(1,len(gamestate)):
		if gamestate[i] == player:
			play_conq.append(i)
		elif gamestate[i] == opponent:
			oppo_conq.append(i)
		else:
			un_conq.append(i)	
	return play_conq, oppo_conq, un_conq
				
def DefineOpponent(player):
	if player == 'X':
		return 'O'
	else:
		return 'X'

def EvalFunc(player, opponent, sq_index, player_conquered, opponent_conquered, sub=0):
	global boardvalue
	p_total = 0
	o_total = 0

	for i in player_conquered:
		p_total += boardvalue[i]
	for i in opponent_conquered:
		o_total += boardvalue[i]
	
	return (boardvalue[sq_index] + p_total - o_total)
	
def MovesForRaid(player_conquered):
	availablemoves = []
	for sq in player_conquered:
		if sq-5 >= 1: #up
			if sq-5 not in availablemoves and sq-5 in unoccupied_sq:
				availablemoves.append(sq-5)
		if sq+5 <=25: #down
			if sq+5 not in availablemoves and sq+5 in unoccupied_sq:
				availablemoves.append(sq+5)
		
		if (sq-1)%5 != 0: #left
			if sq-1 not in availablemoves and sq-1 in unoccupied_sq:
				availablemoves.append(sq-1)
		
		if sq%5 !=0: #right
			if sq+1 not in availablemoves and sq+1 in unoccupied_sq:
				availablemoves.append(sq+1)
	return availablemoves

def MovesForRaidSimul(pc, uc):
	availablemoves = []
	for sq in pc:
		if sq-5 >= 1: #up
			if sq-5 not in availablemoves and sq-5 in uc:
				availablemoves.append(sq-5)
		if sq+5 <=25: #down
			if sq+5 not in availablemoves and sq+5 in uc:
				availablemoves.append(sq+5)
		
		if (sq-1)%5 != 0: #left
			if sq-1 not in availablemoves and sq-1 in uc:
				availablemoves.append(sq-1)
		
		if sq%5 !=0: #right
			if sq+1 not in availablemoves and sq+1 in uc:
				availablemoves.append(sq+1)
	return availablemoves

def ReturnKeyWithMaxVal(dict):
	v=list(dict.values())
	k=list(dict.keys())
	return k[v.index(max(v))]

def EvaluationForRaid(raidmoves, player, opponent):
	global opponent_conquered, player_conquered
		
	if len(raidmoves) == 0: #test this
		return (-99999, None)
	
	convert_opp = {0:[0,0,0]}
	eval_raid = {}
	for sq in raidmoves:
		convert_opp[sq] = [0]
		eval_raid[sq] = 0
	for sq in raidmoves:
		if sq-5 >= 1: #up
			if sq-5 in opponent_conquered:
				convert_opp[sq].append(sq-5)
		if sq+5 <=25: #down
			if sq+5 in opponent_conquered:
				convert_opp[sq].append(sq+5)
		
		if (sq-1)%5 != 0: #left
			if sq-1 in opponent_conquered:
				convert_opp[sq].append(sq-1)
		
		if sq%5 !=0: #right
			if sq+1 in opponent_conquered:
				convert_opp[sq].append(sq+1)
		nuts = EvalFunc(player, opponent, sq, player_conquered, opponent_conquered)
		if sq in convert_opp:
			opp_sqs = convert_opp[sq]
			for x in opp_sqs:
				nuts+= 2*boardvalue[x]
		eval_raid[sq] = nuts
	
	od = collections.OrderedDict(sorted(eval_raid.items()))
	bestRaidMove = ReturnKeyWithMaxVal(od)
	conquerlist = [bestRaidMove] + convert_opp[bestRaidMove]
	return (eval_raid[bestRaidMove], conquerlist)

def EvaluationForRaidSimul(raidmoves, player, opponent, oc, pc):
		
	if len(raidmoves) == 0: #test this
		return (-99999, None)
	
	convert_opp = {0:[0,0,0]}
	eval_raid = {}
	for sq in raidmoves:
		convert_opp[sq] = [0]
		eval_raid[sq] = 0
	for sq in raidmoves:
		if sq-5 >= 1: #up
			if sq-5 in oc:
				convert_opp[sq].append(sq-5)
		if sq+5 <=25: #down
			if sq+5 in oc:
				convert_opp[sq].append(sq+5)
		
		if (sq-1)%5 != 0: #left
			if sq-1 in oc:
				convert_opp[sq].append(sq-1)
		
		if sq%5 !=0: #right
			if sq+1 in oc:
				convert_opp[sq].append(sq+1)
		nuts = EvalFunc(player, opponent, sq, pc, oc)
		if sq in convert_opp:
			opp_sqs = convert_opp[sq]
			for x in opp_sqs:
				nuts+= 2*boardvalue[x]
		eval_raid[sq] = nuts
	
	od = collections.OrderedDict(sorted(eval_raid.items()))
	bestRaidMove = ReturnKeyWithMaxVal(od)
	conquerlist = [bestRaidMove] + convert_opp[bestRaidMove]
	return (eval_raid[bestRaidMove], conquerlist)
	
def EvaluteForMinMax(player, opponent, move, player_conquered, opponent_conquered):
	global raidmoves, sneakmoves
	
	if move in raidmoves:
		convert_opp = []
		if move-5 >= 1: #up
			if move-5 in opponent_conquered:
				convert_opp.append(move-5)
		if move+5 <=25: #down
			if move+5 in opponent_conquered:
				convert_opp.append(move+5)
		
		if (move-1)%5 != 0: #left
			if move-1 in opponent_conquered:
				convert_opp.append(move-1)
		
		if move%5 !=0: #right
			if move+1 in opponent_conquered:
				convert_opp.append(move+1)
				
		nuts = EvalFunc(player, opponent, move, player_conquered, opponent_conquered)
		if len(convert_opp) != 0:
			for x in convert_opp:
				nuts+= 2*boardvalue[x]
		return nuts
	
	else:
		nuts = EvalFunc(player, opponent, move, player_conquered, opponent_conquered)		

def EvaluationForSneak(sneakmoves, player, opponent):
	global opponent_conquered, player_conquered
	if len(sneakmoves) == 0:
		return (-99999, None)
	max_eval = -99999
	bestSneakMove = 99
	for sq in sneakmoves:
		if sq != 0:
			eval = EvalFunc(player, opponent, sq, player_conquered, opponent_conquered)
			if(eval> max_eval):
				max_eval = eval
				bestSneakMove = sq
			elif eval == max_eval:
				if bestSneakMove > sq:
					bestSneakMove = sq
	return (max_eval, bestSneakMove)

def EvaluationForSneakSimul(sneakmoves, player, opponent, oc, pc):
	if len(sneakmoves) == 0:
		return (-99999, None)
	max_eval = -99999
	bestSneakMove = 99
	for sq in sneakmoves:
		if sq != 0:
			eval = EvalFunc(player, opponent, sq, pc, oc)
			if(eval> max_eval):
				max_eval = eval
				bestSneakMove = sq
			elif eval == max_eval:
				if bestSneakMove > sq:
					bestSneakMove = sq
	return (max_eval, bestSneakMove)

def IsRaidBetter(eRaid, eSneak, raidlist, sneakmove):
	if eRaid > eSneak:
		return raidlist
	elif eSneak > eRaid:
		return [sneakmove]
	else:
		#when they are equal
		if raidlist and raidlist != [None]:
			for sq in raidlist:
				if sq<sneakmove and sq != 0:
					return raidlist
			return [sneakmove]

def CaptureSquares(movelist, player):
	global unoccupied_sq
	if movelist and movelist != [None]:
		for sq in movelist:
			gamestate[sq] = player
		unoccupied_sq = list(set(unoccupied_sq) - set(movelist))
		
def WriteNextStateOutput(gamestate):
	with open("next_state.txt", "w") as fp:
		for x in range(0,5):
			for each in gamestate[1+(5*x):6+(5*x)]:
				fp.write(each)
			fp.write("\n")

def WriteNextStateOutputSimul(gamestate, fp):
		for x in range(0,5):
			for each in gamestate[1+(5*x):6+(5*x)]:
				fp.write(each)
			fp.write("\n")
		
def UseGreedySearchAlgo(raidmoves, sneakmoves, player, opponent_conquered, opponent):
	global gamestate
	eRaid, sq_conquer_raid = EvaluationForRaid(raidmoves, player, opponent)
	eSneak, sq_conquer_sneak = EvaluationForSneak(sneakmoves, player, opponent)
	moves = IsRaidBetter(eRaid, eSneak, sq_conquer_raid, sq_conquer_sneak)
	CaptureSquares(moves, player)
	WriteNextStateOutput(gamestate)

def UseGreedySearchAlgoSimul(raidmoves, sneakmoves, player, oc, opponent, pc):
	global gamestate
	eRaid, sq_conquer_raid = EvaluationForRaidSimul(raidmoves, player, opponent, oc, pc)
	eSneak, sq_conquer_sneak = EvaluationForSneakSimul(sneakmoves, player, opponent, oc, pc)
	moves = IsRaidBetter(eRaid, eSneak, sq_conquer_raid, sq_conquer_sneak)
	CaptureSquares(moves, player)
	#WriteNextStateOutput(gamestate)

def GetMinimum(x,y):
	if x<y:
		return x
	else:
		return y
	
def GetMaximum(x,y):
	if x>y:
		return x
	else:
		return y

def IsGameOver(unoccupied_sq):
	if len(unoccupied_sq) == 0:
		return True
	else:
		return False

def WriteToTraverseLog(xnode):
	global labeldict
	if IsSimulation(inputfile) == True:
		return
	str1 = ""
	if xnode.cscore == float('-inf'):
		score = "-Infinity"
	elif xnode.cscore == float('inf'):
		score = "Infinity"
	else:
		score = xnode.cscore
	str1 = labeldict[xnode.clast_captured_sq] + "," + str(xnode.cdepth) + "," + str(score)
	file.write("\n")
	file.write(str1)

def WriteToTraverseLogAB(xnode, alpha, beta):
	global labeldict
	str1 = ""
	if IsSimulation(inputfile) == True:
		return
	if xnode.cscore == float('-inf'):
		score = "-Infinity"
	elif xnode.cscore == float('inf'):
		score = "Infinity"
	else:
		score = xnode.cscore
	str1 = labeldict[xnode.clast_captured_sq] + "," + str(xnode.cdepth) + "," + str(score) + "," + (str("-Infinity") if(alpha == float('-inf')) else str(alpha)) +"," + (str("Infinity") if(beta == float('inf')) else str(beta))
	file.write("\n")
	file.write(str1)
	
def EvaluateForOpponent(pnode): #node has player values ocap will be opponent's
	opponent_moved = pnode.clast_captured_sq
	avail_raids = pnode.craidmoves
	avail_sneaks = pnode.csneakmoves
	player_cap = pnode.cpcaptured
	
	if opponent_moved in avail_raids:
		convert_pl = []
		if opponent_moved-5 >= 1: #up
			if opponent_moved-5 in player_cap:
				convert_pl.append(opponent_moved-5)
		if opponent_moved+5 <=25: #down
			if opponent_moved+5 in player_cap:
				convert_pl.append(opponent_moved+5)
		
		if (opponent_moved-1)%5 != 0: #left
			if opponent_moved-1 in player_cap:
				convert_pl.append(opponent_moved-1)
		
		if opponent_moved%5 !=0: #right
			if opponent_moved+1 in player_cap:
				convert_pl.append(opponent_moved+1)
		nuts = EvalFunc(pnode.cplayer, pnode.copponent, 0, player_cap, pnode.cocaptured)
		for each in convert_pl:
			nuts -= 2*boardvalue[each]
		return nuts
	elif opponent_moved in avail_sneaks:
		nuts = EvalFunc(pnode.cplayer, pnode.copponent, 0, player_cap, pnode.cocaptured)
		return nuts
			
def EvaluateForPlayer(node): #node has opponent values pcap will be opponent's
	player_moved = node.clast_captured_sq
	avail_raids = node.craidmoves
	avail_sneaks = node.csneakmoves
	opponent_cap = node.cpcaptured
	if player_moved in avail_raids:
		convert_opp = []
		if player_moved-5 >= 1: #up
			if player_moved-5 in opponent_cap:
				convert_opp.append(player_moved-5)
		if player_moved+5 <=25: #down
			if player_moved+5 in opponent_cap:
				convert_opp.append(player_moved+5)
		
		if (player_moved-1)%5 != 0: #left
			if player_moved-1 in opponent_cap:
				convert_opp.append(player_moved-1)
		
		if player_moved%5 !=0: #right
			if player_moved+1 in opponent_cap:
				convert_opp.append(player_moved+1)
		nuts = EvalFunc(node.copponent, node.cplayer, 0, node.cocaptured, opponent_cap)
		for each in convert_opp:
			nuts += 2*boardvalue[each]
		return nuts
		
	elif player_moved in avail_sneaks:
		nuts = EvalFunc(node.copponent, node.cplayer, 0, node.cocaptured, opponent_cap)
		return nuts
	
def UpdateRaidMovePieces(ynode):
	#Update if it was a raid move (note player raided and this node is opponent)
	sq_conq = ynode.clast_captured_sq
	raid_plays = ynode.craidmoves
	opponent_sqs = ynode.cpcaptured
	if sq_conq in raid_plays:
		convert_op = []
		if sq_conq-5 >= 1: #up
			if sq_conq-5 in opponent_sqs:
				convert_op.append(sq_conq-5)
		if sq_conq+5 <=25: #down
			if sq_conq+5 in opponent_sqs:
				convert_op.append(sq_conq+5)
		
		if (sq_conq-1)%5 != 0: #left
			if sq_conq-1 in opponent_sqs:
				convert_op.append(sq_conq-1)
		
		if sq_conq%5 !=0: #right
			if sq_conq+1 in opponent_sqs:
				convert_op.append(sq_conq+1)
		if len(convert_op) != 0:
			ynode.cocaptured += convert_op
		 	ynode.cpcaptured = list(set(ynode.cpcaptured) - set(convert_op))
	
def max_play(childPlayerPlay):
	if (IsGameOver(childPlayerPlay.cavailable_moves) or childPlayerPlay.cdepth == cutoff):
		x = EvaluateForOpponent(childPlayerPlay)
		childPlayerPlay.UpdateScore(x)
		WriteToTraverseLog(childPlayerPlay)
		return x
	UpdateRaidMovePieces(childPlayerPlay)
	WriteToTraverseLog(childPlayerPlay)
	best_move = childPlayerPlay.cavailable_moves[0]
	best_score = float('-inf')
	for player_move in childPlayerPlay.cavailable_moves:
		newavailablemoves = childPlayerPlay.GetNextState(player_move)
		depth = childPlayerPlay.GetDepth()+1
		pcap_new = childPlayerPlay.cpcaptured + [player_move]
		childopponent = Node(newavailablemoves, float('inf'), player_move, depth, childPlayerPlay.cocaptured, pcap_new, opponent, player)
		score = min_play(childopponent)
		childopponent.UpdateScore(score)
		if score>best_score:
			best_score = score
			best_move = player_move
			childPlayerPlay.UpdateScore(best_score)
		WriteToTraverseLog(childPlayerPlay)
	return best_score
		
def min_play(childOpponentPlay):
	if (IsGameOver(childOpponentPlay.cavailable_moves) or childOpponentPlay.cdepth == cutoff):
		x = EvaluateForPlayer(childOpponentPlay)
		childOpponentPlay.UpdateScore(x)
		WriteToTraverseLog(childOpponentPlay)
		return x
	#Update if it was a raid move (note player raided and this node is opponent)
	UpdateRaidMovePieces(childOpponentPlay)
	WriteToTraverseLog(childOpponentPlay)
	best_move = childOpponentPlay.cavailable_moves[0]
	best_score = float('inf')
	for opponent_move in childOpponentPlay.cavailable_moves:
		newavailablemoves = childOpponentPlay.GetNextState(opponent_move)
		depth = childOpponentPlay.GetDepth()+1
		ocap_new = childOpponentPlay.cpcaptured + [opponent_move]
		childplayer = Node(newavailablemoves, float('-inf'), opponent_move, depth, childOpponentPlay.cocaptured, ocap_new, player, opponent)
		score = max_play(childplayer)
		childplayer.UpdateScore(score)
		if score<best_score:
			best_score = score
			best_move = opponent_move
			childOpponentPlay.UpdateScore(best_score)
		WriteToTraverseLog(childOpponentPlay)
	return best_score
	
def ApplyMiniMaxAlgo(avail_sq, playerCap, OppoCap):
	if not avail_sq:
		return 0 #Terminate with the given state
	
	root = Node(avail_sq, float('-inf'), 0, 0, playerCap, OppoCap, player, opponent)
	WriteToTraverseLog(root)
	best_move = avail_sq[0]
	best_score = float('-inf')
	for rootmove in avail_sq:
		newavailmoves = root.GetNextState(rootmove)
		pcap_new = playerCap + [rootmove]
		parent = Node(newavailmoves, float('inf'), rootmove, 1, OppoCap, pcap_new, opponent, player)
		score = min_play(parent)
		parent.UpdateScore(score)

		if score>best_score:
			best_score = score
			best_move = rootmove
			root.UpdateScore(best_score)			
		WriteToTraverseLog(root)
	return best_move
	
def ReturnRaidedOpponents(move):
		convert_op = []
		if move-5 >= 1: #up
			if move-5 in opponent_conquered:
				convert_op.append(move-5)
		if move+5 <=25: #down
			if move+5 in opponent_conquered:
				convert_op.append(move+5)
		
		if (move-1)%5 != 0: #left
			if move-1 in opponent_conquered:
				convert_op.append(move-1)
		
		if move%5 !=0: #right
			if move+1 in opponent_conquered:
				convert_op.append(move+1)
			
		return convert_op

def ReturnRaidedOpponentsSimul(move, oc):
		convert_op = []
		if move-5 >= 1: #up
			if move-5 in oc:
				convert_op.append(move-5)
		if move+5 <=25: #down
			if move+5 in oc:
				convert_op.append(move+5)
		
		if (move-1)%5 != 0: #left
			if move-1 in oc:
				convert_op.append(move-1)
		
		if move%5 !=0: #right
			if move+1 in oc:
				convert_op.append(move+1)
			
		return convert_op
	
def max_value(childPlayerPlay, alpha, beta):
	if (IsGameOver(childPlayerPlay.cavailable_moves) or childPlayerPlay.cdepth == cutoff):
		#x = EvaluateForPlayer(childPlayerPlay)
		x = EvaluateForOpponent(childPlayerPlay)
		childPlayerPlay.UpdateScore(x)
		WriteToTraverseLogAB(childPlayerPlay, alpha, beta)
		return x
	
	UpdateRaidMovePieces(childPlayerPlay)
	WriteToTraverseLogAB(childPlayerPlay, alpha, beta)
	best_move = childPlayerPlay.cavailable_moves[0]
	best_score = float('-inf')
	v = float('-inf')
	for player_move in childPlayerPlay.cavailable_moves:
		newavailablemoves = childPlayerPlay.GetNextState(player_move)
		depth = childPlayerPlay.GetDepth()+1
		pcap_new = childPlayerPlay.cpcaptured + [player_move]
		childopponent = Node(newavailablemoves, float('inf'), player_move, depth, childPlayerPlay.cocaptured, pcap_new, opponent, player)
		#WriteToTraverseLog(childopponent)
		score = min_value(childopponent, alpha, beta) #v as alpha
		v = GetMaximum(v, score)

		if v >= beta:
			childPlayerPlay.UpdateScore(v)
			WriteToTraverseLogAB(childPlayerPlay, alpha, beta)
			break
		childPlayerPlay.UpdateScore(v)
		alpha = GetMaximum(alpha, v)
		WriteToTraverseLogAB(childPlayerPlay, alpha, beta) #- new update
	return v
		
def min_value(childOpponentPlay, alpha, beta):
	if (IsGameOver(childOpponentPlay.cavailable_moves) or childOpponentPlay.cdepth == cutoff):
		x = EvaluateForPlayer(childOpponentPlay)
		childOpponentPlay.UpdateScore(x)
		WriteToTraverseLogAB(childOpponentPlay, alpha, beta)
		return x
	#Update if it was a raid move (note player raided and this node is opponent)
	UpdateRaidMovePieces(childOpponentPlay)
	WriteToTraverseLogAB(childOpponentPlay, alpha, beta)
	best_move = childOpponentPlay.cavailable_moves[0]
	best_score = float('inf')
	v = float('inf')
	for opponent_move in childOpponentPlay.cavailable_moves:
		newavailablemoves = childOpponentPlay.GetNextState(opponent_move)
		depth = childOpponentPlay.GetDepth()+1
		ocap_new = childOpponentPlay.cpcaptured + [opponent_move]
		childplayer = Node(newavailablemoves, float('-inf'), opponent_move, depth, childOpponentPlay.cocaptured, ocap_new, player, opponent)
		#WriteToTraverseLog(childplayer)	
		score = max_value(childplayer, alpha, beta)
		v = GetMinimum(v, score)
		#childplayer.UpdateScore(v)
		#WriteToTraverseLog(childplayer) - new update
		if v <= alpha:
			childOpponentPlay.UpdateScore(v)
			WriteToTraverseLogAB(childOpponentPlay, alpha, beta)
			break#return v
		#else:
		#	best_score = score
		#	best_move = opponent_move
			#update child with new best score and write to log
		childOpponentPlay.UpdateScore(v)
		beta = GetMinimum(beta, v)
		WriteToTraverseLogAB(childOpponentPlay, alpha, beta)	#- new update	
	return v
def ApplyAlphaBetaPruningAlgo(avail_sq, playerCap, OppoCap):
	if not avail_sq:
		return 0 #Terminate with the given state
	
	root = Node(avail_sq, float('-inf'), 0, 0, playerCap, OppoCap, player, opponent, float('-inf'), float('inf'))
	best_move = avail_sq[0]
	best_score = float('-inf')
	v = float('-inf')
	alpha = float('-inf')
	beta = float('inf')
	WriteToTraverseLogAB(root, alpha, beta)
	for rootmove in avail_sq:
		newavailmoves = root.GetNextState(rootmove)
		pcap_new = playerCap + [rootmove]
		parent = Node(newavailmoves, float('inf'), rootmove, 1, OppoCap, pcap_new, opponent, player, float('-inf'), float('inf'))
		score = min_value(parent, alpha, beta)
		v = GetMaximum(v, score)
		parent.UpdateScore(score)
		if v>=beta:
			break
		alpha = GetMaximum(alpha, v)
		if score>best_score:
			best_score = score
			best_move = rootmove
		root.UpdateScore(v)
		WriteToTraverseLogAB(root, alpha, beta)
	return best_move

def IsSimulation(filepath):
	with open(filepath, "r") as fp:
		if int(fp.readline().strip()) == 4:
			return True
		return False
	return False

def SimulatePlayerMoves(player, algo, cutoff):
	global boardvalue, gamestate
	opponent = DefineOpponent(player)
	player_conquered, opponent_conquered, unoccupied_sq = UpdateConqueredSquaresSimul(gamestate, player, opponent)
	raidmoves = MovesForRaidSimul(player_conquered, unoccupied_sq)
	sneakmoves = list(set(unoccupied_sq) - set(raidmoves))
	if algo == 1:
		UseGreedySearchAlgoSimul(raidmoves, sneakmoves, player, opponent_conquered, opponent, player_conquered)
	elif algo == 2:
		#with open("traverse_log.txt", "w") as file:
			#file.write("Node,Depth,Value")
			best_move = ApplyMiniMaxAlgo(unoccupied_sq, player_conquered, opponent_conquered)
			if best_move in raidmoves:
				oppto_conq = ReturnRaidedOpponentsSimul(best_move, opponent_conquered) + [best_move]
			else:
				oppto_conq = [best_move]
			CaptureSquares(oppto_conq, player)
			#WriteNextStateOutput(gamestate)
	elif algo == 3:
		#with open("traverse_log.txt", "w") as file:
			#file.write("Node,Depth,Value,Alpha,Beta")
			best_move = ApplyAlphaBetaPruningAlgo(unoccupied_sq, player_conquered, opponent_conquered)
			if best_move in raidmoves:
				oppto_conq = ReturnRaidedOpponents(best_move) + [best_move]
			else:
				oppto_conq = [best_move]
			CaptureSquares(oppto_conq, player)
			#WriteNextStateOutput(gamestate)	

def GetUnoccupiedSq(gamestate):
	unoccupied = []
	for i in range(1,len(gamestate)):
		if gamestate[i] == '*':
			unoccupied.append(i)
	return unoccupied
		
###############################################################
################### MAIN EXECUTION ############################
if IsSimulation(inputfile) == False:
	f= OpenInputFile(inputfile)
	ReadCurrentGameState(f)
	opponent = DefineOpponent(player)
	player_conquered, opponent_conquered, unoccupied_sq = UpdateConqueredSquares(gamestate, player, opponent)
	raidmoves = MovesForRaid(player_conquered)
	sneakmoves = list(set(unoccupied_sq) - set(raidmoves))
	if algo == 1:
		UseGreedySearchAlgo(raidmoves, sneakmoves, player, opponent_conquered, opponent)
	elif algo == 2:
		with open("traverse_log.txt", "w") as file:
			file.write("Node,Depth,Value")
			best_move = ApplyMiniMaxAlgo(unoccupied_sq, player_conquered, opponent_conquered)
			if best_move in raidmoves:
				oppto_conq = ReturnRaidedOpponents(best_move) + [best_move]
			else:
				oppto_conq = [best_move]
			CaptureSquares(oppto_conq, player)
			WriteNextStateOutput(gamestate)
	elif algo == 3:
		with open("traverse_log.txt", "w") as file:
			file.write("Node,Depth,Value,Alpha,Beta")
			best_move = ApplyAlphaBetaPruningAlgo(unoccupied_sq, player_conquered, opponent_conquered)
			if best_move in raidmoves:
				oppto_conq = ReturnRaidedOpponents(best_move) + [best_move]
			else:
				oppto_conq = [best_move]
			CaptureSquares(oppto_conq, player)
			WriteNextStateOutput(gamestate)	
	f.close()
else:
	f = OpenInputFile(inputfile)
	file = open("trace_state.txt", "w")
	p1, p1_algo, p1_cutoff = "", 0, 0
	p2, p2_algo, p2_cutoff = "", 0, 0
	ReadGame(f)
	while (IsGameOver(GetUnoccupiedSq(gamestate)) == False):
		player = p1
		cutoff = p1_cutoff
		algo = p1_algo
		opponent = DefineOpponent(player)
		count += 1
		SimulatePlayerMoves(player, algo, cutoff)
		WriteNextStateOutputSimul(gamestate, file)
		if IsGameOver(GetUnoccupiedSq(gamestate)) == False:
			player = p2
			cutoff = p2_cutoff
			algo = p2_algo
			opponent = DefineOpponent(player)
			SimulatePlayerMoves(player, algo, cutoff)
			count += 1
			WriteNextStateOutputSimul(gamestate, file)
	file.close()
	f.close()
	

################################################################

			
		