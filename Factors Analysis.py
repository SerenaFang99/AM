from jqdatasdk import *
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
auth('13511059588','0011qqQQ')

# 本代码为了简化运算量，使用2018年日数据
factors = ['Turnover', 'PE', 'MarketCap', 'Capitalization', 'EPS',\
           'ROE', 'NI_Growth_Ratio']
Fields = ['turnover_ratio', 'pe_ratio', 'market_cap', 'capitalization',\
          'eps', 'roe', 'inc_net_profit_year_on_year'] 
# 取出因子
# 得到fdate当天股票池中全A股的因子数据
def get_factors(fdate, factors):
    stockList = get_index_stocks('000002.XSHG',fdate)
    factors_list = query(valuation.code, valuation.turnover_ratio, \
                         valuation.pe_ratio, valuation.market_cap, \
                         valuation.capitalization, indicator.eps, \
                         indicator.roe, indicator.inc_net_profit_year_on_year\
                         ).filter(valuation.code.in_(stockList))
    stocks_fundamentals = get_fundamentals(factors_list, date=fdate) # 找到对应的因子数据
    stocks_fundamentals = stocks_fundamentals.set_index(['code'])
    return stocks_fundamentals

# 使用date_list记录开盘日期
def get_period_date(start_date, end_date):
    date_list = []
    current_date = start_date
    delta = datetime.timedelta(days=1)
    end_d = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    current_d = datetime.datetime.strptime(current_date,'%Y-%m-%d')
    while (end_d-current_d).days >= 0:
        week_day = current_d.weekday()
        if week_day != 5 and week_day != 6:
            date_list.append(current_d.strftime('%Y-%m-%d'))
        current_d += delta
    return date_list

# 使用2018年数据
# 当然此处简单修改一下就可以包含更多年份
start_date = '2018-01-01'
end_date = '2018-12-31'
date_list = get_period_date(start_date, end_date)
factorData = {}
for date in date_list:
    # 按日期存储因子数据
    # factorData是全A股股票因子数据
    factorData[date] = get_factors(date,factors) 
        
# 下面开始计算暴露度
def get_exposure(index):
    if index == 'SH50':
        index = '000016.XSHG'  
    if index == 'HS300':
        index = '000300.XSHG'
    if index == 'ZZ500':
        index = '000905.XSHG'
    expo = pd.DataFrame(index = date_list)
    for i in Fields:
        tempExposure = []
        for date in date_list:
            # 取出指数股票池中股票
            stockList = get_index_stocks(index, date)
            # 取出每日因子i
            temp = factorData[date][[i]]
            # 按照i因子降序排列
            temp = temp.sort_values([i],ascending = False)
            # 排序赋值
            temp['rank'] = range(len(temp)+1, 1, -1)
            # 获取指数因子排序平均值
            index_mean = temp.loc[stockList,'rank'].mean()
            # 全市场排序中间值
            middle = len(temp)//2
            # 得到暴露度
            tempExposure.append((index_mean-middle)/len(temp))
        expo[i] = tempExposure
    return expo

result_SH50 = []
result_HS300 = []
result_ZZ500 = []
expo1 = get_exposure('SH50')
expo2 = get_exposure('HS300')
expo3 = get_exposure('ZZ500')
for i in Fields:
    result_SH50.append(expo1[i].mean())
    result_HS300.append(expo2[i].mean())
    result_ZZ500.append(expo3[i].mean())

fig = plt.figure(figsize=(15,6))
bar_width = 0.3
x = np.array(range(len(result_SH50)))
plt.bar(x, result_SH50, bar_width, label = 'SH50')
plt.bar(x+bar_width, result_HS300, bar_width, label = 'HS300')
plt.bar(x+bar_width+bar_width, result_ZZ500, bar_width, label = 'ZZ500')
plt.xticks(range(len(result_SH50)), factors)
plt.legend()
plt.show()


fig1 = plt.figure()
x = np.array(range(len(result_SH50)))
plt.barh(x, result_SH50)
plt.yticks(range(len(result_SH50)), factors)
plt.title('SH50')
plt.show()

fig2 = plt.figure()
x = np.array(range(len(result_HS300)))
plt.barh(x, result_HS300)
plt.yticks(range(len(result_HS300)), factors)
plt.title('HS300')
plt.show()

fig3 = plt.figure()
x = np.array(range(len(result_ZZ500)))
plt.barh(x, result_ZZ500)
plt.yticks(range(len(result_ZZ500)), factors)
plt.title('ZZ500')
plt.show()

# 相关分析
def getCorr(index):
    if index == 'SH50':
        index = '000016.XSHG'
    if index == 'HS300':
        index = '000300.XSHG'
    corr = {}
    for date in date_list:
        stockList = get_index_stocks(index, date)
        temp = factors_data[date].loc[stockList,:]
        corr[date] = temp.corr()
    corr = pd.Panel.from_dict(corr)
    return corr
corr_SH50 = getCorr('SH50')
corr_HS300 = getCorr('HS300')

fig = plt.figure(figsize=(15,6))
ax = fig.add_subplot(111)
sns.heatmap(corr_SH50.mean(axis=0), annot=True, vmax=1, vmin=-0.5, cmap="Blues")
ax.set_title("SH50-Correlation Mean", fontsize=21)
fig.show()

fig = plt.figure(figsize=(15,6))
ax = fig.add_subplot(111)
sns.heatmap(corr_HS300.mean(axis=0), annot=True, vmax=1, vmin=-0.5, cmap="Blues")
ax.set_title("HS300-Correlation Mean", fontsize=21)
fig.show()

fig = plt.figure(figsize=(15,6))
ax = fig.add_subplot(111)
sns.heatmap(corr_SH50.std(axis=0), annot=True, vmax=0.1, vmin=0, cmap="Blues")
ax.set_title("SH50-Correlation Standard Deviation", fontsize=21)
fig.show()

fig = plt.figure(figsize=(15,6))
ax = fig.add_subplot(111)
sns.heatmap(corr_SH50.mean(axis=0)/corr_SH50.std(axis=0), annot=True, vmax=5, vmin=-5, cmap="Blues")
ax.set_title("SH50-Correlation Intensity", fontsize=21)
fig.show()