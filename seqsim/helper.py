from PIL import Image, ImageDraw, ImageFont
import sys
from math import pi, floor
from seqsim.classes import Recovery, Coordinates
from numpy import \
    linspace, empty, transpose, max, min, cos, sin, \
    array as arraynp, isnan, sqrt, arange, zeros, nansum
from itertools import groupby
from scipy.optimize import minimize_scalar as FindMin
from numpy.matlib import repmat


LogScanner = 'Driver={SQL Server};' \
             'Server=192.168.3.55;' \
             'Database=SequalLogScanner;' \
             'UID=sa;' \
             'PWD=gg8976@;'


# Change coordinates from polar to cartesian system
def pol2cart(thetas, rhos, zs):
    X = rhos * cos(thetas)  # Get X coords
    Y = rhos * sin(thetas)  # Get Y coords
    Offset = [
        ((max(X)+min(X))/2),
        ((max(Y)+min(Y))/2)
    ]  # Offset so centre of log is (0,0)
    return Coordinates(X, Y, zs, Offset)


# given the recovery of each board, return total timber value per log
def CalcBoardVol(log, c, r):
    # Initialisations
    if c.HSNum > 0:
        cbW = arraynp(c[37:(37+c.HSNum+1)])  # HoriSaw widths
    else:
        cbW = c.CBWidth
    cbNum = c.CBNum
    cbT = arraynp(c[14:(14+cbNum)])  # CB Thicknesses
    if log.Length > 4400:
        gl = 4.6
    else:
        gl = 4

    # Wingboard volumes
    bVol = 0
    bVol += c.PrimOutWidth*c.PrimOutThick*gl*(
        sum(r.WB["PrimOutR"])+sum(r.WB["PrimOutL"]))
    bVol += c.PrimInWidth*c.PrimInThick*gl*(
        sum(r.WB["PrimInR"])+sum(r.WB["PrimInL"]))
    bVol += c.SecOutWidth*c.SecOutThickT*gl*(sum(r.WB["SecOutT"]))
    bVol += c.SecInWidth*c.SecInThickT*gl*(sum(r.WB["SecInT"]))
    bVol += c.SecOutWidth*c.SecOutThickB*gl*(sum(r.WB["SecOutB"]))
    bVol += c.SecInWidth*c.SecInThickB*gl*(sum(r.WB["SecInB"]))

    for i in range(cbNum):
        if isnan(r.WB["CentreWB"][i]):
            if c.HSNum > 0:
                bVol += sum(r.CB[i]*cbW*cbT[i]*gl)
            else:
                if len(r.CB[i]) > 0:
                    bVol += r.CB[i][0]*c.CBWidth*cbT[i]*gl
        else:
            bVol += r.WB["CentreWB"][i]*cbT[i]*c.CBWidth*gl

    return (bVol/1000000)


def EvalRecovery(pos, coords, r):
    temp = Coordinates(
        coords.X, coords.Y, coords.Z,
        (coords.Offset[0]+pos, coords.Offset[1])
    )
    r.RunRecovery(temp)
    sumR = SumRecov(r)
    return -sumR


# Evaluating how good recovery is
def SumRecov(recovery):
    rSum = 0
    for k in recovery.WB.keys():
        rSum += nansum(recovery.WB[k])
    for i in recovery.CB:
        if isinstance(i, list):
            rSum += nansum(i)
        elif not isnan(i):
            rSum += i
    return rSum


# given the cutplan and coordinates of log, find offset for optimum recovery
def OptBoardPos(coords, c):
    w = max(coords.X)/10
    r = Recovery(c)

    opt = FindMin(EvalRecovery, bounds=(-w, w), method='bounded',
                  options={'xatol': 0.05}, args=(coords, r))
    coords.Offset[0] += opt.x
    return opt


# returns the coordinates for the log inputted with optimum offset based on c
def GetLogCoords(log, c, Opt=True):
    # Set up SED and LED circle coordinates in polar coordinates
    # AveSED = (log.SED+log.MinSED)/2
    # AveLED = (log.LED+log.MaxLED)/2
    # =========================================================================
    #     SEDpts = linspace(log.MinSED/2, log.SED/2, 26)
    #     LEDpts = linspace(log.LED/2, log.MaxLED/2, 26)
    #     SEDpts = hstack((SEDpts, SEDpts[-2::-1]))
    #     SEDpts = hstack((SEDpts, SEDpts[-2::-1]))
    #     LEDpts = hstack((LEDpts, LEDpts[-2::-1]))
    #     LEDpts = hstack((LEDpts, LEDpts[-2::-1]))
    #     z = linspace(0, log.Length, 50)
    #
    #     rhos = empty((SEDpts.shape[0], z.shape[0]))
    #     for i in range(SEDpts.shape[0]):
    #         # coordinates through the log with taper, in polar coordinates
    #         rhos[i, ] = linspace(SEDpts[i], LEDpts[i], z.shape[0])
    #
    #     thetas = transpose(repmat(linspace(0, 2*pi, 101), 50, 1))
    #     zs = repmat(z, 101, 1)
    # =========================================================================
    swPos = 1/3*log.Length
    z = arange(0, log.Length, 100)
    thetas = linspace(0, 2*pi, 100)
    cos2 = cos(thetas)*cos(thetas)
    sin2 = sin(thetas)*sin(thetas)
    a = log.SED/2
    b = (log.MinSED+log.SED)/4
    if isnan(log.MinSED):
        b = log.SED/2
    rhosS = (a*b)/sqrt(b*b*cos2 + a*a*sin2)
    a = (log.MaxLED+log.LED)/4
    b = log.LED/2
    rhosL = (a*b)/sqrt(b*b*cos2 + a*a*sin2)
    rhos = empty((rhosS.shape[0], z.shape[0]))
    for i in range(rhosS.shape[0]):
        # coordinates through the log with taper, in polar coordinates
        rhos[i, ] = linspace(rhosS[i], rhosL[i], z.shape[0])
    thetas = transpose(repmat(thetas, len(z), 1))
    zs = repmat(z, rhosS.shape[0], 1)

    coords = pol2cart(thetas, rhos, zs)

    sweepY = 0
    if log.CompSweep > 0:
        # =====================================================================
        #         sweepY = interp1d(
        #             [0, log.Length/2, log.Length],
        #             [0, log.CompSweep*log.SED*0.01, 0]
        #         )(coords.Z)
        # =====================================================================
        a = -(log.CompSweep*log.SED*0.04)/(log.Length*log.Length)
        sweepY = a*coords.Z*(coords.Z-log.Length)

    def f_sweep(x):
        X = zeros(x.shape)
        a = -(log.Sweep*log.SED*0.01)/(swPos*swPos)
        i = x[x <= swPos]
        X[x <= swPos] = a*i*(i-2*swPos)
        a = (log.Sweep*log.SED*0.01)/(
            (swPos-log.Length)*(log.Length-swPos))
        i = x[x > swPos]
        X[x > swPos] = a*(i-log.Length)*(i-2*swPos+log.Length)
        return X

# =============================================================================
#     sweepX = interp1d(
#         [0, swPos, log.Length],
#         [0, log.Sweep*log.SED*0.01, 0],
#         kind='quadratic'
#     )(coords.Z)
# =============================================================================
    sweepX = f_sweep(coords.Z)

    coords.X += sweepX
    coords.Y += sweepY

    if Opt:
        OptBoardPos(coords, c)

    return coords


def print_progress(
    iteration, total, prefix='', suffix='', decimals=1, bar_length=100
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration  (Required): current iteration (Int)
        total      (Required): total iterations (Int)
        prefix     (Optional): prefix string (Str)
        suffix     (Optional): suffix string (Str)
        decimals   (Optional): +ve number of decimals in percent complete (Int)
        bar_length (Optional): character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    prtStr = '\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)

    if iteration == total:
        prtStr += '\n'

    return prtStr


# keep track to work out how much longer simulation will take
def Timer(ic, il, total, elapsed, tl=1000):
    count = il
    t = (elapsed/count) * (total-count)
    tmin = floor(t/60)
    tsec = round(t % 60)
    if tmin > 0:
        tStr = \
            r'Time Remaining: {:d} min(s) {:d} sec(s)'.format(tmin, tsec)
    else:
        tStr = r'Time Remaining: {:d} sec(s)'.format(tsec)
    prtStr = print_progress(
        count, total,
        prefix="Cutplan "+str(ic[0])+" of "+str(ic[1])+":",
        suffix=" "+tStr+"          "
    )

    sys.stdout.write(prtStr)
    sys.stdout.flush()


def DrawCutplan(conn, c, id, colour=(255, 255, 255),
                folder="images\\cps\\",
                gradImg="images\\gradient.png",
                highlight=True, logs=None):
    if logs is None:
        logs = c.LogCount

    wh = 500
    s = wh/(float(c.Description[2:4])*10+50)

    img = Image.new('RGBA', (wh, wh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    DrawPrimary(c, draw, wh, s, colour)

    DrawSecondary(c, draw, wh, s, colour)

    DrawCB(c, draw, wh, s, colour)

    fullimg = Image.new('RGBA', (wh, wh))
    circ = Image.new('RGBA', (wh, wh))
    draw = ImageDraw.Draw(circ)
    draw.ellipse((0, 0, wh, wh), (255, 255, 255))

    gradient = Image.open(gradImg)
    fullimg = Image.composite(gradient, fullimg, circ)
    fullimg = Image.alpha_composite(fullimg, img)

    if highlight:
        h_fullimg = Image.new('RGBA', (wh, wh))
        circ = Image.new('RGBA', (wh, wh))
        draw = ImageDraw.Draw(circ)
        draw.ellipse((0, 0, wh, wh), (255, 255, 255))
        h_fullimg = Image.composite(gradient, h_fullimg, circ)
        font = ImageFont.truetype("tahomabd.ttf", 45)
        font2 = ImageFont.truetype("tahoma.ttf", 39)
        draw = ImageDraw.Draw(h_fullimg)
        tw, th = draw.textsize(c.Description, font=font)
        lstr = str(logs) + " logs"
        tw2, th2 = draw.textsize(lstr, font=font2)
        draw.text(
            ((wh-tw)/2, (wh-th-th2)/2),
            c.Description, (0, 115, 119), font=font)
        draw.text(((wh-tw2)/2, (wh+th-th2)/2), lstr, (0, 115, 119), font=font2)
        h_fullimg = Image.blend(fullimg, h_fullimg, 0.65)

    fullimg.save(folder+'CP'+str(id)+'.png', 'PNG')
    if highlight:
        h_fullimg.save(folder+'CP'+str(id)+'_h.png', 'PNG')


def DrawPrimary(c, draw, wh, s, colour):
    cantW = c.CBWidth

    def getXY(x, y, w, h):
        xy = [
            ((wh-w*s)/2+x*s, (wh-h*s)/2+y*s), ((wh+w*s)/2+x*s, (wh+h*s)/2+y*s)
        ]
        return xy

    def drawRecX(x1, w1, h1, k):
        if w1 > 0:
            draw.rectangle(getXY(-x1-w1/2-k, 0, w1, h1), colour)  # left
            draw.rectangle(getXY(x1+w1/2+k, 0, w1, h1), colour)  # right
            return (x1+w1+k)
        return x1

    cW = cantW/2
    cW = drawRecX(cW, c.PrimInThick, c.PrimInWidth, c.PrimInK)
    if (c.PrimInSplit):
        cW = drawRecX(cW, c.PrimInThick, c.PrimInWidth, c.PrimSplitK)

    cW = drawRecX(cW, c.PrimOutThick, c.PrimOutWidth, c.PrimOutK)
    if (c.PrimOutSplit):
        cW = drawRecX(cW, c.PrimOutThick, c.PrimOutWidth, c.PrimSplitK)


def DrawSecondary(c, draw, wh, s, colour):
    cantH = sum(c[14:24]) + c.SecK*(c.CBNum-1)

    def getXY(x, y, w, h):
        xy = [
            ((wh-w*s)/2+x*s, (wh-h*s)/2+y*s), ((wh+w*s)/2+x*s, (wh+h*s)/2+y*s)
        ]
        return xy

    def drawRecY(y1, w1, h1, k, tb):
        if h1 > 0:
            draw.rectangle(getXY(0, tb*(y1+h1/2+k), w1, h1), colour)
            return (y1+h1+k)
        return y1

    cH = cantH/2
    cH = drawRecY(cH, c.SecInWidth, c.SecInThickT, c.SecK, -1)
    if (c.SecInSplitT):
        cH = drawRecY(cH, c.SecInWidth, c.SecInThickT, c.SecK, -1)

    cH = drawRecY(cH, c.SecOutWidth, c.SecOutThickT, c.SecK, -1)
    if (c.SecOutSplitT):
        cH = drawRecY(cH, c.SecOutWidth, c.SecOutThickT, c.SecK, -1)

    cH = cantH/2
    cH = drawRecY(cH, c.SecInWidth, c.SecInThickB, c.SecK, 1)
    if (c.SecInSplitB):
        cH = drawRecY(cH, c.SecInWidth, c.SecInThickB, c.SecK, 1)

    cH = drawRecY(cH, c.SecOutWidth, c.SecOutThickB, c.SecK, 1)
    if (c.SecOutSplitB):
        cH = drawRecY(cH, c.SecOutWidth, c.SecOutThickB, c.SecK, 1)


def DrawCB(c, draw, wh, s, colour):
    cantH = sum(c[14:24]) + c.SecK*(c.CBNum-1)
    cantW = c.CBWidth

    def getXY(x, y, w, h):
        xy = [
            ((wh-w*s)/2+x*s, (wh-h*s)/2+y*s), ((wh+w*s)/2+x*s, (wh+h*s)/2+y*s)
        ]
        return xy

    cH = 0
    hsK = list(c[41:])
    hsK.append(0)
    for i in range(c.CBNum):
        cW = 0
        if (c.HSNum > 0):
            for j in range(c.HSNum+1):
                draw.rectangle(
                    getXY(-cantW/2+cW+c[37+j]/2,
                          -cantH/2+cH+c[14+i]/2,
                          c[37+j], c[14+i]), colour)
                cW += c[37+j] + hsK[j]
        else:
            draw.rectangle(
                getXY(-cantW/2+cW+c.CBWidth/2,
                      -cantH/2+cH+c[14+i]/2,
                      c.CBWidth, c[14+i]), colour)
        cH += c[14+i] + c.SecK


def ConvertBoards(tempC, i, prefix, suffix=""):
    sp = prefix
    tb = suffix

    if tempC.loc[i, sp+'InThick'+tb] > 0:
        if tempC.loc[i, sp+'OutThick'+tb] > 0:
            if tempC.loc[i, sp+'OutSplit'+tb]:
                tempC.loc[i, sp+'OutThick'+tb] -= 1
            else:
                tempC.loc[i, sp+'OutThick'+tb] -= 0.5
            tempC.loc[i, sp+'InThick'+tb] -= 1
        else:
            if tempC.loc[i, sp+'InSplit'+tb]:
                tempC.loc[i, sp+'InThick'+tb] -= 1
            else:
                tempC.loc[i, sp+'InThick'+tb] -= 0.5


def ConvertCutplans(Cutplan, ChangeBV=False):
    tempC = Cutplan.copy()

    for i in range(tempC.shape[0]):
        # tempC.loc[i, 'COLUMN'] = VALUE

        # PRIMARY
        ConvertBoards(tempC, i, "Prim")

        # SECONDARY TOP
        ConvertBoards(tempC, i, "Sec", "T")

        # SECONDARY BOT
        ConvertBoards(tempC, i, "Sec", "B")

        # CENTREBOARDS
        if tempC.loc[i, 'PrimInThick'] > 0:
            tempC.loc[i, 'CBWidth'] -= 0.5
        for j in range(10):
            if tempC.loc[i, 'CBThick'+str(j+1)] > 0:
                tempC.loc[i, 'CBThick'+str(j+1)] -= 1
        for j in range(4):
            if tempC.loc[i, 'HorWidth'+str(j+1)] > 0:
                tempC.loc[i, 'HorWidth'+str(j+1)] -= 0.5

        if ChangeBV:
            c = tempC.iloc[i]

            bVol = c.PrimInThick*(c.PrimInSplit+1)*c.PrimInWidth*2
            bVol += c.PrimOutThick*(c.PrimOutSplit+1)*c.PrimOutWidth*2
            bVol += c.SecInThickT*(c.SecInSplitT+1)*c.SecInWidth
            bVol += c.SecOutThickT*(c.SecOutSplitT+1)*c.SecOutWidth
            bVol += c.SecInThickB*(c.SecInSplitB+1)*c.SecInWidth
            bVol += c.SecOutThickB*(c.SecOutSplitB+1)*c.SecOutWidth

            cbs = list(c[14:(14+c.CBNum)])
            count = [sum(1 for j in g) for _, g in groupby(cbs)]
            cbNum = max(count)
            index = [j for j in range(len(count)) if count[j] == cbNum]
            start = sum(count[i] for i in range(index[floor(len(index)/2)]))
            for j in range(c.CBNum):
                if (j >= start) and (j < start+cbNum) and (c.HSNum > 0):
                    for k in list(c[37:(37+c.HSNum+1)]):
                        bVol += cbs[j]*k
                else:
                    bVol += cbs[j]*c.CBWidth

            bL = (int(c.Description[5:7])-1)/10.0
            bVol /= 1000000
            bVol *= bL

            tempC.loc[i, 'BoardVol'] = bVol

    return tempC
