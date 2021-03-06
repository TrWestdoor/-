import numpy as np
import matplotlib.pyplot as plt


# sec7-6, programing sec7-4 code, which is a adaptive load file data function.
def loadDataSet(fileName):
    numFeat = len(open(fileName).readline().strip().split('\t'))
    dataMat = []
    labelMat = []
    fr = open(fileName)
    for line in fr.readlines():
        lineArr = []
        curLine = line.strip().split('\t')
        for i in range(numFeat-1):
            lineArr.append(float(curLine[i]))
        dataMat.append(lineArr)
        labelMat.append(float(curLine[-1]))
    fr.close()
    return dataMat, labelMat


def loadSimpData():
    datMat = np.array([[1. , 2.1],
                     [2. , 1.1],
                     [1.3, 1. ],
                     [1. , 1. ],
                     [2. , 1. ]])
    classLabels = [1.0, 1.0, -1.0, -1.0, 1.0]
    return datMat, classLabels


def stumpClassify(dataMatrix, dimen, threashVal, threshIneq):
    retArray = np.ones((np.shape(dataMatrix)[0], 1))
    if threshIneq == 'lt':
        retArray[dataMatrix[:, dimen] <= threashVal] = -1.0
    else:
        retArray[dataMatrix[:, dimen] > threashVal] = -1.0
    return retArray


def buildStump(dataArr, classLabels, D):
    dataMatrix = np.mat(dataArr)
    labelMat = np.mat(classLabels).T
    m, n = np.shape(dataMatrix)
    numSteps = 10.0
    bestStump = {}
    bestClasEst = np.mat(np.zeros((m, 1)))
    minError = np.inf
    # Recurrent each dimension.
    for i in range(n):
        rangeMin = dataMatrix[:, i].min()
        rangeMax = dataMatrix[:, i].max()
        stepSize = (rangeMax - rangeMin) / numSteps

        # Recurrent all value according stepSize in this dimension.
        for j in range(-1, int(numSteps)+1):
            # Two judge way.
            for inequal in ['lt', 'gt']:
                threshVal = (rangeMin + float(j) * stepSize)

                # stumpClassify: Return an array which is classify result.
                predictedVals = stumpClassify(dataMatrix, i, threshVal, inequal)
                errArr = np.mat(np.ones((m, 1)))
                errArr[predictedVals == labelMat] = 0
                weightedError = D.T * errArr
                # print("split: dim %d, thresh %.2f, thresh inequal: %s, the weighted error is %.3f" % \
                #       (i, threshVal, inequal, weightedError))
                if weightedError < minError:
                    minError = weightedError
                    bestClasEst = predictedVals.copy()
                    bestStump['dim'] = i
                    bestStump['thresh'] = threshVal
                    bestStump['ineq'] = inequal
    return bestStump, minError, bestClasEst


def adaBoostTrainDS(dataArr, classLables, numIt=40):
    weakClassArr = []
    m = np.shape(dataArr)[0]
    D = np.mat(np.ones((m, 1)) / m)
    # aggClassEst: Record class aggregate value in each data point.
    aggClassEst = np.mat(np.zeros((m, 1)))
    for i in range(numIt):
        bestStump, error, classEst = buildStump(dataArr, classLables, D)
        # print("D: ", D.T)

        alpha = float(0.5*np.log((1.0 - error) / max(error, 1e-16)))
        bestStump['alpha'] = alpha
        weakClassArr.append(bestStump)
        # print("classEst: ", classEst.T)

        # exp_on: Combine the both of two condition for classify result,
        # exp_on = - alpha * f(x) * h_t(x)  //f(x) is label, h_t(x) is predict result at D_t distribution.
        # update D distribution.
        exp_on = np.multiply(-1*alpha*np.mat(classLables).T, classEst)
        D = np.multiply(D, np.exp(exp_on))
        D = D/D.sum()
        aggClassEst += alpha*classEst
        # print("aggClassEst: ", aggClassEst.T)

        aggErrors = np.multiply(np.sign(aggClassEst) != np.mat(classLables).T, np.ones((m, 1)))
        errorRate = aggErrors.sum() / m
        print("total error: ", errorRate, "\n")
        if errorRate == 0.0:
            break
    # primary return value:
    # return weakClassArr

    # For plot ROC curve:
    return weakClassArr, aggClassEst


def adaClassify(datToClass, classifierArr):
    dataMatrix = np.mat(datToClass)
    m = np.shape(dataMatrix)[0]
    aggClassEst = np.mat(np.zeros((m, 1)))
    for i in range(len(classifierArr)):
        classEst = stumpClassify(dataMatrix, classifierArr[i]['dim'],
                                 classifierArr[i]['thresh'],
                                 classifierArr[i]['ineq'])
        aggClassEst += classifierArr[i]['alpha'] * classEst
        # print(aggClassEst)
    return np.sign(aggClassEst)


def plotROC(predStrengths, classLabels):
    cur = (1.0, 1.0)
    ySUm = 0.0
    numPosClas = sum(np.array(classLabels) == 1.0)
    yStep = 1/float(numPosClas)
    xStep = 1/float(len(classLabels) - numPosClas)
    sortedIndicies = predStrengths.argsort()
    fig = plt.figure()
    fig.clf()
    ax = plt.subplot(111)
    for index in sortedIndicies.tolist()[0]:
        # y_label will decrease yStep when the index-th sample is positive, which means that TP number will
        # decrease before this index.
        if classLabels[index] == 1.0:
            delX = 0
            delY = yStep
        # x_label will decrease xStep because a negative sample was found.
        else:
            delX = xStep
            delY = 0
            ySUm += cur[1]
        ax.plot([cur[0], cur[0]-delX], [cur[1], cur[1]-delY], c='b')
        cur = (cur[0]-delX, cur[1]-delY)
    ax.plot([0, 1], [0, 1], 'b--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curve for AdaBoost Horse Colic Detection System')
    ax.axis([0, 1, 0, 1])
    plt.show()
    print("the Area Under the Curve is: ", ySUm * xStep)


def main():
    datMat, classLabels = loadSimpData()
    # In p121
    # D = np.mat(np.ones((5, 1)) / 5)
    # print(buildStump(datMat, classLabels, D))
    ###################

    # programming 7-2
    # classifierArray = adaBoostTrainDS(datMat, classLabels, 9)
    # print(classifierArray)

    # sec7-5, programming 7-3 example
    # datArr, labelArr = loadSimpData()
    # classifierArr = adaBoostTrainDS(datArr, labelArr, 30)
    # print("classify result: ", adaClassify([0, 0], classifierArr))
    # print("classify result: ", adaClassify([[5, 5], [0, 0]], classifierArr))

    # sec7-6, programming 7-4 example
    # datArr, labelArr = loadDataSet('horseColicTraining2.txt')
    # classifierArray = adaBoostTrainDS(datArr, labelArr, 10)
    # testArr, testLabelArr = loadDataSet('horseColicTest2.txt')
    # prediction10 = adaClassify(testArr, classifierArray)
    # errArr = np.mat(np.ones((len(testArr), 1)))
    # err_num = errArr[prediction10 != np.mat(testLabelArr).T].sum()
    # print("error rate: ", err_num / len(testArr))

    # sec7-7.1, programming 7-5 example
    datArr, labelArr = loadDataSet('horseColicTraining2.txt')
    classifierArray, aggClassEst = adaBoostTrainDS(datArr, labelArr, 50)
    plotROC(aggClassEst.T, labelArr)


if __name__ == '__main__':
    main()
