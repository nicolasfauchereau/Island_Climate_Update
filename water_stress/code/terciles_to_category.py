def terciles_to_category(df, colnames=['T1','T2','T3'], mindiff=10, climdiff=5): 
    """
    convert a tercile probabilistic forecast into a categorical forecast
    
    if the difference between the maximum probability and the next one is >= mindiff 
    (10 is default) then it's either 'ABOVE', 'NEAR NORMAL' or 'BELOW' depending on the max 
    probability 
    
    if the difference between consecutive probabilities is less than mindiff (10)
    but greater than climdiff (5) then we end up with either 'AVG - BELOW' or 'AVG - ABOVE'
    
    if the difference between consecutive probabilities is less than 5%, it's a CLIMATOLOGY 
    forecasts 
    """
    
    T1, T2, T3 = colnames
    
    cats = []
    for i, row in df.iterrows(): 
        fcst = row.loc[colnames,].astype('int')
        if (fcst.idxmax()  == T3) & ((fcst.loc[T3] - fcst.loc[T2]) >= mindiff): 
            cat = 'ABOVE'
        elif (fcst.idxmax()  == T3) & ((fcst.loc[T3] - fcst.loc[T2]) < mindiff) & ((fcst.loc[T3] - fcst.loc[T2]) > climdiff):
            cat = 'AVG - ABOVE'
        elif (fcst.idxmax()  == T1) & ((fcst.loc[T1] - fcst.loc[T2]) >= mindiff):
            cat = 'BELOW'
        elif (fcst.idxmax()  == T1) & ((fcst.loc[T1] - fcst.loc[T2]) < mindiff) & ((fcst.loc[T1] - fcst.loc[T2]) > climdiff):
            cat = 'AVG - BELOW'
        elif (fcst.idxmax()  == T2) & ((fcst.loc[T2] - fcst.loc[T1]) >= mindiff) & ((fcst.loc[T2] - fcst.loc[T3]) >= mindiff): 
            cat = 'NEAR NORMAL'
        else: 
            cat = 'CLIMATOLOGY'
        cats.append(cat)
    return np.array(cats)
