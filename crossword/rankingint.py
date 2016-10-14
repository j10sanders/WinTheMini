def toint(day_rank):
    strranking = []
    for day in day_rank:
       strranking.append(str(day))
    for dayresult in strranking:
        strranking = [dayresult.replace(',', "").replace('(', "").replace(')', "") for dayresult in strranking]
    ranking = []
    for string in strranking:
        ranking.append(int(string))
    return ranking
            
def tointplain(ywinner):
    strranking = []
    for z in ywinner:
       strranking.append(str(z))
    for dayresult in strranking:
        strranking = [dayresult.replace(',', "").replace('(', "").replace(')', "") for dayresult in strranking]
    for s in strranking:
        int(s)
    return s