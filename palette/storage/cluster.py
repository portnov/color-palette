
import numpy as np

try: 
    from pylab import imread
    from sklearn.cluster import MeanShift, estimate_bandwidth
    from sklearn.utils import shuffle

    print("Image loading is available")
    image_loading_supported = True

except ImportError:

    image_loading_supported = False
    print("Image loading is not available")

if image_loading_supported:

    from color.colors import *

    def get_common_colors(filename, N=1000):
        image = imread(filename)
        w,h,d = tuple(image.shape)
        image_array = np.array( np.reshape(image, (w * h, d)), dtype=np.float64 )
        if image.dtype == 'uint8':
            image_array = image_array / 255.0
        image_array_sample = shuffle(image_array, random_state=0)[:N]
        bandwidth = estimate_bandwidth(image_array_sample, quantile=0.01, n_samples=500)
        ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
        ms.fit(image_array_sample)
        cluster_centers = ms.cluster_centers_
        n_clusters = len(cluster_centers)
        colors = []
        print("Number of clusters: {}".format(n_clusters))
        for x in cluster_centers:
            #print x
            clr = Color()
            clr.setRGB1((x[0], x[1], x[2]))
            colors.append(clr)
        return colors
