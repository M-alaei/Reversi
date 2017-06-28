
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

TOKEN = "Your Bot Token"
updater = Updater(TOKEN)
playerTile,botTile = [' ',' ']
mainBoard = []
chatIds = []
turn = []
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def printBoard(bot,update,board):
    query = update.callback_query
    keyboard = []
    for i in range(8):
        keyboard.append([])
        for j in range(8):
            keyboard[i].append(InlineKeyboardButton(board[i][j], callback_data='%s%s'%(i,j)))

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=query.message.chat_id, text="Select a Blank Square :",reply_markup=reply_markup)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def initialBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = '     '
    board[3][3] = '⚪️'
    board[3][4] = '⚫️'
    board[4][3] = '⚫️'
    board[4][4] = '⚪️'
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def newBoard():
   board = []
   for i in range(8):
       board.append(['     '] * 8)
   return board

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def isOnBoard(x,y):
    result = x>=0 and x<=7 and y>=0 and y<=7
    return result
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def whoGoesFirst():
    if random.randint(0, 1) == 0:
         return 'bot'
    else:
         return 'you'
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def isValidMove(board, tile, xstart, ystart):
	 if board[xstart][ystart] != '     ' or not isOnBoard(xstart, ystart):
		 return False

	 board[xstart][ystart] = tile
	 if tile == '⚪️':
		 otherTile = '⚫️'
	 else:
		 otherTile = '⚪️'

	 tilesToFlip = []
	 for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
		 x, y = xstart, ystart
		 x += xdirection
		 y += ydirection
		 if isOnBoard(x, y) and board[x][y] == otherTile:
			 x += xdirection
			 y += ydirection
			 if not isOnBoard(x, y):
				 continue
			 while board[x][y] == otherTile:
				 x += xdirection
				 y += ydirection
				 if not isOnBoard(x, y):
					 break
			 if not isOnBoard(x, y):
				 continue
			 if board[x][y] == tile:
				 while True:
					 x -= xdirection
					 y -= ydirection
					 if x == xstart and y == ystart:
						 break
					 tilesToFlip.append([x, y])

	 board[xstart][ystart] ='     '
	 if len(tilesToFlip) == 0:
		 return False
	 return tilesToFlip

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetBoardHasblankCheck(board):
        for x in range(8):
            for y in range(8):
                if board[x][y] == '     ':
                    return True
        return False
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetValidMoves(board, tile):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetBoardWithValidMoves(board, tile):
     dupeBoard = GetBoardCopy(board)
     for x, y in GetValidMoves(dupeBoard, tile):
         dupeBoard[x][y] = '✅'
     return dupeBoard
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetBoardCopy(board):
     dupeBoard = newBoard()
     for x in range(8):
         for y in range(8):
             dupeBoard[x][y] = board[x][y]
     return dupeBoard
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == '⚪️':
                xscore += 1
            if board[x][y] == '⚫️':
                oscore += 1
    return {'⚪️':xscore, '⚫️':oscore}

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def makeMove(board, tile, xstart, ystart):

    tilesToFlip = isValidMove(board, tile, xstart, ystart)
    if board[xstart][ystart] == '     ' and isOnBoard(xstart, ystart):
        board[xstart][ystart] = tile
    if tilesToFlip == False:
        return False
    for x, y in tilesToFlip:
        board[x][y] = tile

    return True
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def isOnCorner(x, y):
     return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def GetComputerMove(board, botTile):
        possibleMoves = GetValidMoves(board, botTile)
        random.shuffle(possibleMoves)
        for x, y in possibleMoves:
            if isOnCorner(x, y):
                return [x, y]

        # bestScore = -1
        # for x, y in possibleMoves:
        #     dupeBoard = GetBoardCopy(board)
        #     makeMove(dupeBoard, botTile, x, y)
        #     score = GetScoreOfBoard(dupeBoard)[botTile]
        #     if score <= bestScore:
        #         bestMove = [x, y]
        #         bestScore = score
        # print(bestMove)
        bestMove = []
        if(possibleMoves !=[]):
            bestMove = random.choice(possibleMoves);
        return bestMove
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def EndOfGame(playerTile,botTile,mainboard,bot,update):
    query = update.callback_query
    scores = GetScoreOfBoard(mainboard)
    if scores[playerTile]>scores[botTile]:
        bot.send_message(chat_id=query.message.chat_id, text='You Win!! by %s points! Congratulations! press /playAgain to play Again'% (scores[playerTile] - scores[botTile]))
        print('player %s won!!!'%query.message.chat_id)
    elif scores[playerTile]<scores[botTile]:
        bot.send_message(chat_id=query.message.chat_id, text='You lost!! The computer beat you by %s points. press /playAgain to play Again' % (scores[botTile] - scores[playerTile]))
        print('bot won!!!')
    else:
        bot.send_message(chat_id=query.message.chat_id, text='The game was a tie! press /playAgain to play Again')
        print('The game with player %s was a tie!'%query.message.chat_id)
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def start(bot, update):
        print("-"*100)
        print("user joined with info : %s" % update.message.from_user)
        print("-"*100)
        player =  [[InlineKeyboardButton("⚪️", callback_data='P1'),
                    InlineKeyboardButton("⚫️", callback_data='P2')]]
        reply_markup = InlineKeyboardMarkup(player)
        update.message.reply_text('Do you want to be ⚪️ or ⚫️?', reply_markup=reply_markup)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def UpdateGame(bot, update):
    query = update.callback_query
    tile = ''
    tile = query.data
    index = ''
    global turn ,mainBoard, showHints, botTile,playerTile,chatIds
    if query.message.chat_id in chatIds:
        index = chatIds.index(query.message.chat_id)
    else:
        chatIds.append(query.message.chat_id)
        index = chatIds.index(query.message.chat_id)
    if tile == 'P1' or tile == 'P2':
        mainBoard.append(newBoard())
        initialBoard(mainBoard[index])
        turn.insert(index,whoGoesFirst())
        if tile == 'P1':
           bot.send_message(chat_id=query.message.chat_id, text="Your Tile is: ⚪️")
           playerTile, botTile = ['⚪️', '⚫️']
        elif tile == 'P2':
           bot.send_message(chat_id=query.message.chat_id, text="Your Tile is: ⚫️")
           playerTile, botTile = ['⚫️', '⚪️']
        if turn[index] == 'bot':
              bot.send_message(chat_id=query.message.chat_id, text="bot turn")
              x, y = GetComputerMove(mainBoard[index], botTile)
              makeMove(mainBoard[index], botTile, x, y)
              turn[index] = 'you'
        bot.edit_message_text(text="Scores :%s"%GetScoreOfBoard(mainBoard[index]),chat_id=query.message.chat_id,message_id=query.message.message_id)
        validMovesBoard = GetBoardWithValidMoves(mainBoard[index], playerTile)
        printBoard(bot,update,validMovesBoard)
    else:
       if turn[index] == 'you':
           move = query.data
           if makeMove(mainBoard[index], playerTile, int(move[0]), int(move[1])) :
               if GetValidMoves(mainBoard[index], botTile) == [] and not GetBoardHasblankCheck(mainBoard[index]):
                   EndOfGame(playerTile,botTile,mainBoard[index],bot,update)
                   return
               turn[index] = 'bot'
               validMove = GetComputerMove(mainBoard[index],botTile)
               if validMove !=[]:
                   makeMove(mainBoard[index], botTile,validMove[0],validMove[1])
               if GetValidMoves(mainBoard[index], botTile) == []  and not GetBoardHasblankCheck(mainBoard[index]) :
                   EndOfGame(playerTile,botTile,mainBoard[index],bot,update)
                   return
           turn[index] = 'you'
           bot.edit_message_text(text="Scores :%s"%GetScoreOfBoard(mainBoard[index]),chat_id=query.message.chat_id,message_id=query.message.message_id)
           validMovesBoard = GetBoardWithValidMoves(mainBoard[index], playerTile)
           printBoard(bot,update,validMovesBoard)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(UpdateGame))
updater.dispatcher.add_handler(CommandHandler('playAgain',start))
updater.start_polling()
updater.idle()
