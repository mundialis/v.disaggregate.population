#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      v.disaggregate.population
# AUTHOR(S):   Guido Riembauer, <riembauer at mundialis.de>
#
# PURPOSE:     Disaggregates population based on vector admin areas, vector
#              urban areas and a high resolution population raster
#
# COPYRIGHT:   (C) 2020-2022 mundialis GmbH & Co. KG, and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#############################################################################
# %Module
# % description: Disaggregates population based on vector admin areas, vector urban areas and a high resolution population raster data.
# % keyword: vector
# % keyword: raster
# % keyword: disaggregation
# %End

# %option G_OPT_V_INPUT
# % key: population_vector
# % type: string
# % required: yes
# % multiple: no
# % label: Vector map containing population to be disaggregated in a column
# %end

# %option
# % key: population_column
# % type: string
# % required: no
# % multiple: no
# % label: Column of input vector map with population information
# %end

# %option G_OPT_R_INPUT
# % key: population_raster
# % type: string
# % required: yes
# % multiple: no
# % label: High resolution population raster map
# %end

# %option G_OPT_R_OUTPUT
# % key: output
# % type: string
# % required: yes
# % multiple: no
# % label: Name of output raster map
# %end

# %option G_OPT_V_INPUT
# % key: urban_vector
# % type: string
# % required: yes
# % multiple: no
# % label: Vector containing urban areas (all other areas must be nodata)
# %end

import atexit
import grass.script as grass
import os

rm_rasters = []


def cleanup():
    nuldev = open(os.devnull, "w")
    kwargs = {"flags": "f", "quiet": True, "stderr": nuldev}
    for rmrast in rm_rasters:
        if grass.find_file(name=rmrast, element="raster")["file"]:
            grass.run_command("g.remove", type="raster", name=rmrast, **kwargs)
    if grass.find_file(name="MASK", element="raster")["file"]:
        try:
            grass.run_command("r.mask", flags="r")
        except:
            pass


def main():
    global rm_rasters

    admin_vector = options["population_vector"]
    column = options["population_column"]
    population_raster = options["population_raster"]
    dense = options["urban_vector"]
    output = options["output"]

    pid = os.getpid()

    # check that v.area.weigh is installed
    if not grass.find_program("v.area.weigh", "--help"):
        grass.fatal(
            _("The 'v.area.weigh' module was not found, install it first:")
            + "\n"
            + "g.extension v.area.weigh"
        )

    # limit calculation to dense urban areas and close small gaps between buildings
    grass.run_command("r.mask", vector=dense)

    temp_grow1 = "%s_grownbyone_%s" % (population_raster, pid)
    rm_rasters.append(temp_grow1)
    temp_grow2 = "%s_shrunkbyone_%s" % (population_raster, pid)
    rm_rasters.append(temp_grow2)
    grass.run_command(
        "r.grow", input=population_raster, output=temp_grow1, radius=1.01
    )
    grass.run_command(
        "r.grow", input=temp_grow1, output=temp_grow2, radius=-1.01
    )
    grass.run_command("r.mask", flags="r")

    # put together areas from inside and outside cities
    pop_raster_new = "pop_raster_temp_%s" % pid
    rm_rasters.append(pop_raster_new)
    grass.run_command(
        "r.mapcalc",
        expression="%s =if(isnull(%s), %s,%s)"
        % (pop_raster_new, population_raster, temp_grow2, population_raster),
    )

    grass.run_command(
        "v.area.weigh",
        vector=admin_vector,
        column=column,
        weight=pop_raster_new,
        output=output,
    )

    grass.message(_("Generated raster <%s>" % output))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
