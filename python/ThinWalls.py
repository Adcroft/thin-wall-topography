from GMesh import GMesh
import numpy

class ThinWalls(GMesh):
    """Container for thin wall topographic data and mesh.

    Additional members:
    zc_simple_mean - mean elevation of cell, shape (nj,ni)
    zu_simple_mean - mean elevation of western edge of cell, shape (nj,ni+1)
    zv_simple_mean - mean elevation of southern edge of cell, shape (nj+1,nj)
    shapeu  - shape of zu_simple_mean, ie. =(nj,ni+1)
    shapev  - shape of zv_simple_mean, ie. =(nj+1,ni)

    Extends the GMesh class.
    """

    def __init__(self, *args, **kwargs):
        """Constructor for ThinWalls."""
        GMesh.__init__(self, *args, **kwargs)
        self.shapeu = (self.nj, self.ni+1)
        self.shapev = (self.nj+1, self.ni)
        self.zc_simple_mean = None
        self.zc_simple_min = None
        self.zc_simple_max = None
        self.zu_simple_mean = None
        self.zu_simple_min = None
        self.zu_simple_max = None
        self.zv_simple_mean = None
        self.zv_simple_min = None
        self.zv_simple_max = None
    def refine(self):
        """Returns new ThinWalls instance with twice the resolution."""
        M = super().refineby2()
        return ThinWalls(lon=M.lon, lat=M.lat)
    def dump(self):
        """Dump Mesh to tty."""
        super().dump()
        print('zc_simple_mean =',self.zc_simple_mean)
        print('zc_simple_min =',self.zc_simple_min)
        print('zc_simple_max =',self.zc_simple_max)
        print('zu_simple_mean =',self.zu_simple_mean)
        print('zu_simple_min =',self.zu_simple_min)
        print('zu_simple_max =',self.zu_simple_max)
        print('zv_simple_mean =',self.zv_simple_mean)
        print('zv_simple_min =',self.zv_simple_min)
        print('zv_simple_max =',self.zv_simple_max)
    def set_cell_mean(self, data):
        """Set elevation of cell center."""
        assert data.shape==self.shape, 'data argument has wrong shape'
        self.zc_simple_mean = data.copy()
    def set_edge_mean(self, datau, datav):
        """Set elevation of cell edges u,v."""
        assert datau.shape==self.shapeu, 'datau argument has wrong shape'
        assert datav.shape==self.shapev, 'datav argument has wrong shape'
        self.zu_simple_mean = datau.copy()
        self.zu_simple_min = datau.copy()
        self.zu_simple_max = datau.copy()
        self.zv_simple_mean = datav.copy()
        self.zv_simple_min = datav.copy()
        self.zv_simple_max = datav.copy()
    def set_center_stats(self):
        """Set stats of center from mean value."""
        self.zc_simple_min = self.zc_simple_mean.copy()
        self.zc_simple_max = self.zc_simple_mean.copy()
    def set_edge_to_step(self):
        """Set elevation of cell edges to step topography."""
        self.zu_simple_mean = numpy.zeros(self.shapeu)
        self.zu_simple_mean[:,1:-1] = numpy.maximum( self.zc_simple_mean[:,:-1], self.zc_simple_mean[:,1:] )
        self.zu_simple_mean[:,0] = self.zc_simple_mean[:,0]
        self.zu_simple_mean[:,-1] = self.zc_simple_mean[:,-1]
        #self.zu_simple_mean[:,0] = numpy.maximum( self.zc_simple_mean[:,0], self.zc_simple_mean[:,-1] )
        #self.zu_simple_mean[:,-1] = numpy.maximum( self.zc_simple_mean[:,0], self.zc_simple_mean[:,-1] )
        self.zu_simple_min = self.zu_simple_mean.copy()
        self.zu_simple_max = self.zu_simple_mean.copy()
        self.zv_simple_mean = numpy.zeros(self.shapev)
        self.zv_simple_mean[1:-1,:] = numpy.maximum( self.zc_simple_mean[:-1,:], self.zc_simple_mean[1:,:] )
        self.zv_simple_mean[0,:] = self.zc_simple_mean[0,:]
        self.zv_simple_mean[-1,:] = self.zc_simple_mean[-1,:]
        #self.zv_simple_mean[0,:] = numpy.maximum( self.zc_simple_mean[0,:], self.zc_simple_mean[-1,:] )
        #self.zv_simple_mean[-1,:] = numpy.maximum( self.zc_simple_mean[0,:], self.zc_simple_mean[-1,:] )
        self.zv_simple_min = self.zv_simple_mean.copy()
        self.zv_simple_max = self.zv_simple_mean.copy()
        if self.zc_simple_min is None: self.set_center_stats()
    def coarsen(self):
        M = ThinWalls(lon=self.lon[::2,::2],lat=self.lat[::2,::2])
        M.zc_simple_mean = 0.25*( (self.zc_simple_mean[::2,::2]+self.zc_simple_mean[1::2,1::2])
                          +(self.zc_simple_mean[::2,1::2]+self.zc_simple_mean[1::2,::2]) )
        M.zc_simple_min = numpy.minimum(
                     numpy.minimum( self.zc_simple_min[::2,::2], self.zc_simple_min[1::2,1::2]),
                     numpy.minimum( self.zc_simple_min[::2,1::2], self.zc_simple_min[1::2,::2]) )
        M.zc_simple_max = numpy.maximum(
                     numpy.maximum( self.zc_simple_max[::2,::2], self.zc_simple_max[1::2,1::2]),
                     numpy.minimum( self.zc_simple_max[::2,1::2], self.zc_simple_max[1::2,::2]) )
        M.zu_simple_mean = 0.5*( self.zu_simple_mean[::2,::2] + self.zu_simple_mean[1::2,::2] )
        M.zu_simple_min = numpy.minimum( self.zu_simple_min[::2,::2], self.zu_simple_min[1::2,::2] )
        M.zu_simple_max = numpy.maximum( self.zu_simple_max[::2,::2], self.zu_simple_max[1::2,::2] )
        M.zv_simple_mean = 0.5*( self.zv_simple_mean[::2,::2] + self.zv_simple_mean[::2,1::2] )
        M.zv_simple_min = numpy.minimum( self.zv_simple_min[::2,::2], self.zv_simple_min[::2,1::2] )
        M.zv_simple_max = numpy.maximum( self.zv_simple_max[::2,::2], self.zv_simple_max[::2,1::2] )
        return M
    def plot(self, axis, thickness=0.2, metric='mean', *args, **kwargs):
        """Plots ThinWalls data."""
        def copy_coord(xy):
            XY = numpy.zeros( (2*self.nj+2,2*self.ni+2) )
            dr = xy[1:,1:] - xy[:-1,:-1]
            dl = xy[:-1,1:] - xy[1:,:-1]
            XY[::2,::2] = xy
            XY[2::2,2::2] = XY[2::2,2::2] - dr*thickness/2
            XY[1::2,::2] = xy
            XY[1:-1:2,2::2] = XY[1:-1:2,2::2] - dl*thickness/2
            XY[::2,1::2] = xy
            XY[2::2,1:-1:2] = XY[2::2,1:-1:2] + dl*thickness/2
            XY[1::2,1::2] = xy
            XY[1:-1:2,1:-1:2] = XY[1:-1:2,1:-1:2] + dr*thickness/2 
            return XY
        lon = copy_coord(self.lon)
        lat = copy_coord(self.lat)
        def pcol_elev(c,u,v):
            tmp = numpy.ma.zeros( (2*self.nj+1,2*self.ni+1) )
            tmp[::2,::2] = numpy.ma.masked # Mask corner values
            tmp[1::2,1::2] = c
            tmp[1::2,::2] = u
            tmp[::2,1::2] = v
            return axis.pcolormesh(lon, lat, tmp, *args, **kwargs)
        if metric is 'mean':
            return pcol_elev( self.zc_simple_mean, self.zu_simple_mean, self.zv_simple_mean )
        elif metric is 'min':
            return pcol_elev( self.zc_simple_min, self.zu_simple_min, self.zv_simple_min )
        elif metric is 'max':
            return pcol_elev( self.zc_simple_max, self.zu_simple_max, self.zv_simple_max )
        else: raise Exception('Unknown "metric"')
    def plot_grid(self, axis, *args, **kwargs):
        """Plots ThinWalls mesh."""
        super().plot(axis, *args, **kwargs)