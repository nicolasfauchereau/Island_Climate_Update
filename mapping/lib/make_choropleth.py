def make_choropleth(ax, df, var='Stress', dict_colors=None):
    """
    makes a choropleth map from
    """

    from shapely.geometry import Point, LineString
    import cartopy.crs as ccrs
    from cartopy.feature import ShapelyFeature

    dateline = LineString([Point(180., -32.), Point(180., 25.)])

    for i, row in df.iterrows():

        v = int(row.loc[var])

        if v == -999:
            color = 'w'
            geom = row.geometry
            sp = ShapelyFeature([geom], ccrs.PlateCarree(),
                                edgecolor='k',
                                facecolor=color, lw=0.5, hatch='//')
        else:

            color = dict_colors[v]

            geom = row.geometry

            sp = ShapelyFeature([geom], ccrs.PlateCarree(),
                                edgecolor='k',
                                facecolor=color, lw=0.5)

            ax.add_feature(sp)

            if geom.intersects(dateline):
                line = geom.intersection(dateline)
                sp = ShapelyFeature([line], ccrs.PlateCarree(), lw=1.05, color=color)
                ax.add_feature(sp)
