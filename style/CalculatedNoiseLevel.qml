<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" maxScale="0" simplifyMaxScale="1" simplifyDrawingTol="1" readOnly="0" simplifyLocal="1" simplifyDrawingHints="1" simplifyAlgorithm="0" labelsEnabled="0" version="3.16.10-Hannover" minScale="100000000">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endField="" durationField="" startExpression="" startField="" mode="0" fixedDuration="0" enabled="0" accumulate="0" durationUnit="min" endExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 forceraster="0" enableorderby="0" symbollevels="0" type="RuleRenderer">
    <rules key="{f1cd36ab-6e63-4971-a889-517e01cf0c67}">
      <rule symbol="0" filter="&quot;dBA_activity&quot; >= 1 AND &quot;dBA_activity&quot; &lt;= 20" label="&lt;10 - 20 dBA" key="{3b205eb1-6c0e-48a1-b616-14700dbf9f6a}"/>
      <rule symbol="1" filter="&quot;dBA_activity&quot; > 20 AND &quot;dBA_activity&quot; &lt;= 30" label=">20 - 30 dBA" key="{20b1ddb4-493a-4bb1-a6a7-ca88f8f1a25e}"/>
      <rule symbol="2" filter="&quot;dBA_activity&quot; > 30 AND &quot;dBA_activity&quot; &lt;= 40" label=">30 - 40 dBA" key="{1d2ca791-8325-4e12-9ec4-85f648069e59}"/>
      <rule symbol="3" filter="&quot;dBA_activity&quot; > 40 AND &quot;dBA_activity&quot; &lt;= 50" label=">40 - 50 dBA" key="{c958a2cd-654b-4a53-986f-bb6bd8cedd55}"/>
      <rule symbol="4" filter="&quot;dBA_activity&quot; > 50 AND &quot;dBA_activity&quot; &lt;= 60" label=">50 - 60 dBA" key="{de1ca2a4-a8a7-46ce-95ef-40895cd94133}"/>
      <rule symbol="5" filter="&quot;dBA_activity&quot; > 60 AND &quot;dBA_activity&quot; &lt;= 70" label=">60 - 70 dBA" key="{424c6e03-fc6a-4f44-84b2-bbbd054446ab}"/>
      <rule symbol="6" filter="&quot;dBA_activity&quot; > 70 AND &quot;dBA_activity&quot; &lt;= 80" label=">70 - 80 dBA" key="{32f14f84-4858-44ce-a508-179f51dac183}"/>
      <rule symbol="7" filter="&quot;dBA_activity&quot; > 80 AND &quot;dBA_activity&quot; &lt;= 90" label=">80 - 90 dBA" key="{6f8b99a8-8445-4122-b5d1-a628884a8135}"/>
      <rule symbol="8" filter="&quot;dBA_activity&quot; > 90 AND &quot;dBA_activity&quot; &lt;= 100" label=">90 - 100 dBA" key="{f1ccd783-7791-4a79-bc3d-ed0bbdd74b69}"/>
      <rule symbol="9" filter="&quot;dBA_activity&quot; > 100 AND &quot;dBA_activity&quot; &lt;= 110" label=">100 - 110 dBA" key="{f9389db9-ccba-48c7-bb3c-00676ff725e4}"/>
      <rule symbol="10" filter="&quot;dBA_activity&quot; > 110 AND &quot;dBA_activity&quot; &lt;= 120" label=">110 - 120 dBA" key="{57f9c255-6bd3-468a-b557-ef113e126d0e}"/>
      <rule symbol="11" filter="&quot;dBA_activity&quot; > 120  AND &quot;dBA_activity&quot; &lt;= 130" label=">120 - 130 dBA" key="{f275adc0-4db6-4d93-b81a-f50fc03ca56c}"/>
      <rule symbol="12" filter="&quot;dBA_activity&quot; > 130  AND &quot;dBA_activity&quot; &lt;= 140" label=">130  -140 dBA" key="{8f94ab49-bd7f-48fb-a4f5-d8654e495268}"/>
      <rule symbol="13" filter=" &quot;dBA_activity&quot; > 140" label=">140 dBA" key="{66fa209b-3e99-426c-a55c-41c57a3785c2}"/>
    </rules>
    <symbols>
      <symbol alpha="1" clip_to_extent="1" name="0" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="1" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,219,219,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="10" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,174,97,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="11" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,147,45,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="12" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,127,0,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,0"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="13" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="122,122,122,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,0"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="2" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,182,182,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="3" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,146,146,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="4" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,83,83,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="5" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="231,232,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="6" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="169,182,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="7" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="93,112,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="8" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="39,68,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" name="9" type="fill" force_rhr="0">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,221,191,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="159,159,159,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property value="false" key="OnConvertFormatRegeneratePrimaryKey"/>
    <property value="&quot;HubName&quot;" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory backgroundAlpha="255" sizeScale="3x:0,0,0,0,0,0" spacingUnitScale="3x:0,0,0,0,0,0" penWidth="0" lineSizeType="MM" showAxis="1" sizeType="MM" direction="0" diagramOrientation="Up" width="15" lineSizeScale="3x:0,0,0,0,0,0" scaleBasedVisibility="0" rotationOffset="270" minScaleDenominator="0" height="15" minimumSize="0" barWidth="5" spacingUnit="MM" opacity="1" enabled="0" spacing="5" backgroundColor="#ffffff" maxScaleDenominator="1e+08" scaleDependency="Area" penColor="#000000" penAlpha="255" labelPlacementMethod="XHeight">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol alpha="1" clip_to_extent="1" name="" type="line" force_rhr="0">
          <layer locked="0" class="SimpleLine" enabled="1" pass="0">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" showAll="1" linePlacementFlags="18" priority="0" zIndex="0" dist="0" placement="1">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option value="0" name="allowedGapsBuffer" type="double"/>
        <Option value="false" name="allowedGapsEnabled" type="bool"/>
        <Option value="" name="allowedGapsLayer" type="QString"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="left">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="top">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="right">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bottom">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_mean">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_min">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_max">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_minority">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_majority">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="id_2">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="landuse">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="elv1">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="HubName">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="HubDist">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dist_m">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_dist">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_src">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_scn">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_reflect">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dur_hr">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="op_hr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dur_percent">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_corrt">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_resultant">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dBA_activity">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="id" name="" index="0"/>
    <alias field="left" name="" index="1"/>
    <alias field="top" name="" index="2"/>
    <alias field="right" name="" index="3"/>
    <alias field="bottom" name="" index="4"/>
    <alias field="_mean" name="" index="5"/>
    <alias field="_min" name="" index="6"/>
    <alias field="_max" name="" index="7"/>
    <alias field="_minority" name="" index="8"/>
    <alias field="_majority" name="" index="9"/>
    <alias field="id_2" name="" index="10"/>
    <alias field="landuse" name="" index="11"/>
    <alias field="elv1" name="" index="12"/>
    <alias field="HubName" name="" index="13"/>
    <alias field="HubDist" name="" index="14"/>
    <alias field="dist_m" name="" index="15"/>
    <alias field="dBA_dist" name="" index="16"/>
    <alias field="dBA_src" name="" index="17"/>
    <alias field="dBA_scn" name="" index="18"/>
    <alias field="dBA_reflect" name="" index="19"/>
    <alias field="dur_hr" name="" index="20"/>
    <alias field="op_hr" name="" index="21"/>
    <alias field="dur_percent" name="" index="22"/>
    <alias field="dBA_corrt" name="" index="23"/>
    <alias field="dBA_resultant" name="" index="24"/>
    <alias field="dBA_activity" name="" index="25"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="id" expression=""/>
    <default applyOnUpdate="0" field="left" expression=""/>
    <default applyOnUpdate="0" field="top" expression=""/>
    <default applyOnUpdate="0" field="right" expression=""/>
    <default applyOnUpdate="0" field="bottom" expression=""/>
    <default applyOnUpdate="0" field="_mean" expression=""/>
    <default applyOnUpdate="0" field="_min" expression=""/>
    <default applyOnUpdate="0" field="_max" expression=""/>
    <default applyOnUpdate="0" field="_minority" expression=""/>
    <default applyOnUpdate="0" field="_majority" expression=""/>
    <default applyOnUpdate="0" field="id_2" expression=""/>
    <default applyOnUpdate="0" field="landuse" expression=""/>
    <default applyOnUpdate="0" field="elv1" expression=""/>
    <default applyOnUpdate="0" field="HubName" expression=""/>
    <default applyOnUpdate="0" field="HubDist" expression=""/>
    <default applyOnUpdate="0" field="dist_m" expression=""/>
    <default applyOnUpdate="0" field="dBA_dist" expression=""/>
    <default applyOnUpdate="0" field="dBA_src" expression=""/>
    <default applyOnUpdate="0" field="dBA_scn" expression=""/>
    <default applyOnUpdate="0" field="dBA_reflect" expression=""/>
    <default applyOnUpdate="0" field="dur_hr" expression=""/>
    <default applyOnUpdate="0" field="op_hr" expression=""/>
    <default applyOnUpdate="0" field="dur_percent" expression=""/>
    <default applyOnUpdate="0" field="dBA_corrt" expression=""/>
    <default applyOnUpdate="0" field="dBA_resultant" expression=""/>
    <default applyOnUpdate="0" field="dBA_activity" expression=""/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" constraints="0" field="id" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="left" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="top" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="right" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="bottom" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="_mean" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="_min" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="_max" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="_minority" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="_majority" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="id_2" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="landuse" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="elv1" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="HubName" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="HubDist" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dist_m" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_dist" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_src" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_scn" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_reflect" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dur_hr" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="op_hr" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dur_percent" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_corrt" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_resultant" unique_strength="0" exp_strength="0"/>
    <constraint notnull_strength="0" constraints="0" field="dBA_activity" unique_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="id" exp=""/>
    <constraint desc="" field="left" exp=""/>
    <constraint desc="" field="top" exp=""/>
    <constraint desc="" field="right" exp=""/>
    <constraint desc="" field="bottom" exp=""/>
    <constraint desc="" field="_mean" exp=""/>
    <constraint desc="" field="_min" exp=""/>
    <constraint desc="" field="_max" exp=""/>
    <constraint desc="" field="_minority" exp=""/>
    <constraint desc="" field="_majority" exp=""/>
    <constraint desc="" field="id_2" exp=""/>
    <constraint desc="" field="landuse" exp=""/>
    <constraint desc="" field="elv1" exp=""/>
    <constraint desc="" field="HubName" exp=""/>
    <constraint desc="" field="HubDist" exp=""/>
    <constraint desc="" field="dist_m" exp=""/>
    <constraint desc="" field="dBA_dist" exp=""/>
    <constraint desc="" field="dBA_src" exp=""/>
    <constraint desc="" field="dBA_scn" exp=""/>
    <constraint desc="" field="dBA_reflect" exp=""/>
    <constraint desc="" field="dur_hr" exp=""/>
    <constraint desc="" field="op_hr" exp=""/>
    <constraint desc="" field="dur_percent" exp=""/>
    <constraint desc="" field="dBA_corrt" exp=""/>
    <constraint desc="" field="dBA_resultant" exp=""/>
    <constraint desc="" field="dBA_activity" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" name="id" type="field" hidden="0"/>
      <column width="-1" name="left" type="field" hidden="0"/>
      <column width="-1" name="top" type="field" hidden="0"/>
      <column width="-1" name="right" type="field" hidden="0"/>
      <column width="-1" name="bottom" type="field" hidden="0"/>
      <column width="-1" name="_sum" type="field" hidden="0"/>
      <column width="-1" name="_mean" type="field" hidden="0"/>
      <column width="-1" name="_stdev" type="field" hidden="0"/>
      <column width="-1" name="_min" type="field" hidden="0"/>
      <column width="-1" name="_max" type="field" hidden="0"/>
      <column width="-1" name="_minority" type="field" hidden="0"/>
      <column width="-1" name="_majority" type="field" hidden="0"/>
      <column width="-1" name="id_2" type="field" hidden="0"/>
      <column width="-1" name="landuse" type="field" hidden="0"/>
      <column width="-1" name="elv1" type="field" hidden="0"/>
      <column width="-1" name="HubName" type="field" hidden="0"/>
      <column width="-1" name="HubDist" type="field" hidden="0"/>
      <column width="-1" name="dist_m" type="field" hidden="0"/>
      <column width="-1" name="dBA_dist" type="field" hidden="0"/>
      <column width="-1" name="dBA_src" type="field" hidden="0"/>
      <column width="-1" name="dBA_scn" type="field" hidden="0"/>
      <column width="-1" name="dBA_reflect" type="field" hidden="0"/>
      <column width="-1" name="dur_hr" type="field" hidden="0"/>
      <column width="-1" name="op_hr" type="field" hidden="0"/>
      <column width="-1" name="dur_percent" type="field" hidden="0"/>
      <column width="-1" name="dBA_corrt" type="field" hidden="0"/>
      <column width="-1" name="dBA_resultant" type="field" hidden="0"/>
      <column width="-1" name="dBA_activity" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="HubDist"/>
    <field editable="1" name="HubName"/>
    <field editable="1" name="_majority"/>
    <field editable="1" name="_max"/>
    <field editable="1" name="_mean"/>
    <field editable="1" name="_min"/>
    <field editable="1" name="_minority"/>
    <field editable="1" name="_stdev"/>
    <field editable="1" name="_sum"/>
    <field editable="1" name="bottom"/>
    <field editable="1" name="dBA_activity"/>
    <field editable="1" name="dBA_corrt"/>
    <field editable="1" name="dBA_dist"/>
    <field editable="1" name="dBA_reflect"/>
    <field editable="1" name="dBA_resultant"/>
    <field editable="1" name="dBA_scn"/>
    <field editable="1" name="dBA_src"/>
    <field editable="1" name="dist_m"/>
    <field editable="1" name="dur_hr"/>
    <field editable="1" name="dur_percent"/>
    <field editable="1" name="elv1"/>
    <field editable="1" name="id"/>
    <field editable="1" name="id_2"/>
    <field editable="1" name="landuse"/>
    <field editable="1" name="left"/>
    <field editable="1" name="op_hr"/>
    <field editable="1" name="right"/>
    <field editable="1" name="top"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="HubDist"/>
    <field labelOnTop="0" name="HubName"/>
    <field labelOnTop="0" name="_majority"/>
    <field labelOnTop="0" name="_max"/>
    <field labelOnTop="0" name="_mean"/>
    <field labelOnTop="0" name="_min"/>
    <field labelOnTop="0" name="_minority"/>
    <field labelOnTop="0" name="_stdev"/>
    <field labelOnTop="0" name="_sum"/>
    <field labelOnTop="0" name="bottom"/>
    <field labelOnTop="0" name="dBA_activity"/>
    <field labelOnTop="0" name="dBA_corrt"/>
    <field labelOnTop="0" name="dBA_dist"/>
    <field labelOnTop="0" name="dBA_reflect"/>
    <field labelOnTop="0" name="dBA_resultant"/>
    <field labelOnTop="0" name="dBA_scn"/>
    <field labelOnTop="0" name="dBA_src"/>
    <field labelOnTop="0" name="dist_m"/>
    <field labelOnTop="0" name="dur_hr"/>
    <field labelOnTop="0" name="dur_percent"/>
    <field labelOnTop="0" name="elv1"/>
    <field labelOnTop="0" name="id"/>
    <field labelOnTop="0" name="id_2"/>
    <field labelOnTop="0" name="landuse"/>
    <field labelOnTop="0" name="left"/>
    <field labelOnTop="0" name="op_hr"/>
    <field labelOnTop="0" name="right"/>
    <field labelOnTop="0" name="top"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"HubName"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
