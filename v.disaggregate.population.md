## DESCRIPTION

*v.disaggregate.population* disaggregates population data from a
administrative boundary vector with population information onto a
high-res raster with estimated local population. A urban area vector is
used to close small gaps in the population raster in high density urban
areas.

## EXAMPLE

```sh
v.disaggregate.population population_vector=admin_areas population_column=POP_2020 population_raster=pop_raster_2020 urban_vector=urban_areas output=pop_raster_2020_disaggregated
```

## SEE ALSO

*[r.grow](https://grass.osgeo.org/grass-stable/manuals/r.grow.html),
[v.area.weigh](v.area.weigh.md) (addon)*

## AUTHOR

Guido Riembauer, [mundialis](https://www.mundialis.de/), Germany
