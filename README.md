# pesticides
## Data sources


[Stanislaus Agricultural Commissioner, PUR up to 2024](https://www.stanag.org/public-information-records.shtm)

[CalPIP](https://calpip.cdpr.ca.gov/main.cfm)
    [State-wide PUR Data Archives, up to 2022](https://files.cdpr.ca.gov/pub/outgoing/pur_archives/)


California Data:
    [Private Schools](https://data-cdegis.opendata.arcgis.com/datasets/d5cb03b3d973473ebb86b24005a0e118_0/explore?location=37.126232%2C-121.546979%2C8.69)

    [Public Schools](https://data-cdegis.opendata.arcgis.com/datasets/61a4260e68b14a5ab91daf27d4415e7d_0/explore?location=37.542678%2C-121.035296%2C10.92)


## To add in future
Data Sources separate page.

Highlight schools/pesticide applications within X distance (Also add population data)

Filter pesticide applications by school day & kind.

Dominant wind direction

select different counties.

Add legend to streamlit folium :
https://stackoverflow.com/questions/77931522/how-to-add-a-legend-to-streamlit-folium-map-when-there-is-few-discrete-colors






## Notes

# Import necessary functions from branca library
from branca.element import Template, MacroElement

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.5);
     border-radius: 6px; padding: 10px; font-size: 10.5px; right: 20px; top: 20px;'>     
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background: green; opacity: 0.75;'></span>Wind speed <= 55.21</li>
    <li><span style='background: yellow; opacity: 0.75;'></span>55.65 <= Wind speed <= 64.29</li>
    <li><span style='background: orange; opacity: 0.75;'></span>64.50 <= Wind speed <= 75.76</li>
    <li><span style='background: red; opacity: 0.75;'></span>75.90 <= Wind speed <= 90.56</li>
    <li><span style='background: purple; opacity: 0.75;'></span>Wind speed >= 91.07</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 18px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 16px; margin-right: 4.5px;}
</style>
{% endmacro %}
"""

# Create a Folium map
map = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=5)

# Add the legend to the map
macro = MacroElement()
macro._template = Template(legend_template)
map.get_root().add_child(macro)

# Display the map
map

