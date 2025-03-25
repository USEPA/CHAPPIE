def get_NLCD(self, year, dataset="Land_Cover"):
        """Download NLCD raster tiles by polygon extent.

        If not lower 48 only run one state at a time

        Parameters
        ----------
        year : integer or string
            Year being retrieved.
        dataset : string
            Valid datasets include Land_Cover, Tree_Canopy, Impervious, or
            roads. The default is "Land_Cover".

        Returns
        -------
        geopandas.GeoDataFrame or array
            Depends on dataset type, array from rasterio
        """
        # Make sure dataset parameter is usable
        datasets = ["Land_Cover", "Impervious", "Tree_Canopy"]
        assert dataset in datasets, f"'{dataset}' not in NLCD datasets"
        # Make sure year parameter is usable
        year = check_year(year, dataset)

        # Create subset X and Y string from extent (minx, miny, maxx, maxy)
        subset = [
            'X("{}","{}")'.format(self.bbox[0], self.bbox[2]),
            'Y("{}","{}")'.format(self.bbox[1], self.bbox[3]),
        ]
        query_crs = self.geom.crs.to_epsg()  # CRS for query

        # Determine landmass (based on FIPs state)
        if not set(self.FIPs.ST_ABBR).isdisjoint(["AK", "HI", "PR"]):
            # TODO: not robust for multi: e.g., non-conus, or conus + non-conus
            landmass = set(self.FIPs.ST_ABBR).intersection(["AK", "HI", "PR"]).pop()
        else:
            landmass = "L48"
        # Determine serviceName
        if dataset == "Tree_Canopy" and landmass == "L48":
            serviceName = f"nlcd_tcc_conus_{year}_v2021-4"
            coverage = "mrlc_download__" + serviceName
        else:
            serviceName = f"NLCD_{year}_{dataset}_{landmass}"
            coverage = serviceName

        # Source url (to use mrlc_display change outCRS to 3857)
        # url = f"https://www.mrlc.gov/geoserver/mrlc_display/{coverage}/ows"
        url = f"https://www.mrlc.gov/geoserver/mrlc_download/{serviceName}/ows"
        epsg_url = "http://www.opengis.net/def/crs/EPSG/0/"
        out_crs = 5070  # Service native(mrlc_display/3857, mrlc_download/5070)

        # Create params dict
        params = {
            "service": "WCS",
            "version": "2.0.1",
            "request": "GetCoverage",
            "coverageid": coverage,
            "subset": subset,
            "SubsettingCRS": f"{epsg_url}{query_crs}",
            "format": "image/geotiff",
            "OutputCRS": "{}{}".format(epsg_url, out_crs),
        }

        # Get response
        res = get_url(url, params)

        # Save result to D1
        out_file = os.path.join(self.D1, f"NLCD_{year}_{dataset}.tif")
        with open(out_file, "wb") as f:
            f.write(res.content)
        self.sl.logger.info(f"Download Succeeded: NLCD_{year}_{dataset}.tif")

        if dataset == "Land_Cover":
            # Vectorize and return gdf in memory
            nlcd_gdf = vectorize(out_file, mask=self.geom["geometry"])
            # Reproject to 3857
            nlcd_gdf = nlcd_gdf.to_crs(3857)
            # set it
            self.set_NLCD(out_file, in_memory=nlcd_gdf)
            return nlcd_gdf
        elif dataset in ["Tree_Canopy", "Impervious"]:
            # Read in raster using rioxarray
            rds = rioxarray.open_rasterio(out_file)
            if not rds.rio.crs:
                # TODO: confirm is none and make more robust?
                rds.rio.set_crs(f"EPSG:{out_crs}")
            cell = rds.rio.resolution()
            rds_prj = rds.rio.reproject(f"EPSG:{3857}", resolution=cell)  # Reproject
            band1 = rds_prj.to_series()  # numpy array
            # save it to D2 (drop after testing?)
            rds_prj.rio.to_raster(f"{self.D2}{os.sep}{os.path.basename(out_file)}")
            # set it
            self.set_NLCD(out_file, in_memory=band1)
        return band1
