<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" maxScale="0" simplifyAlgorithm="0" labelsEnabled="0" simplifyDrawingTol="1" readOnly="0" simplifyMaxScale="1" version="3.16.16-Hannover" minScale="100000000" simplifyDrawingHints="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal mode="0" durationField="" startExpression="" enabled="0" startField="" accumulate="0" endExpression="" durationUnit="min" fixedDuration="0" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="0" symbollevels="0" type="RuleRenderer" forceraster="0">
    <rules key="{e4e29f21-0811-453e-8be0-b06a03107fe4}">
      <rule label="Not Exceed Threshold" symbol="0" key="{28eb4fed-fe60-4e57-ba59-d0fe6150888d}" filter="ELSE"/>
      <rule label="> 45 dBA Residential Threshold" symbol="1" key="{e1c1810c-fad6-484e-9c8e-1ce99291a046}" filter="CASE WHEN &quot;zone&quot; = 'residential' AND &quot;dBA_activity&quot; > 45 THEN &quot;dBA_activity&quot; END"/>
      <rule label="> 70 dBA Industrial Threshold" symbol="2" key="{9b37a89e-dd23-4810-80ba-2e68d5e66660}" filter="CASE WHEN &quot;zone&quot; = 'industrial' AND &quot;dBA_activity&quot; > 70 THEN &quot;dBA_activity&quot; END"/>
    </rules>
    <symbols>
      <symbol type="fill" alpha="1" clip_to_extent="1" name="0" force_rhr="0">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="190,207,80,0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" alpha="1" clip_to_extent="1" name="1" force_rhr="0">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="249,224,27,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" alpha="1" clip_to_extent="1" name="2" force_rhr="0">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="31,120,180,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.06"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property value="false" key="OnConvertFormatRegeneratePrimaryKey"/>
    <property value="&quot;HubName&quot;" key="dualview/previewExpressions"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>2</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks type="StringList">
      <Option type="QString" value=""/>
    </activeChecks>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="id" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="left" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="top" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="right" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bottom" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="_mean" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="_min" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="_max" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="_minority" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="_majority" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="id_2" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="zone" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="elv1" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="HubName" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="HubDist" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dist_m" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_dist" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="soft_percent" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_src" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_scn" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_reflect" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dur_hr" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="op_hr" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dur_percent" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_corrt" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_resultant" configurationFlags="None">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dBA_activity" configurationFlags="None">
      <editWidget type="">
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
    <alias field="zone" name="" index="11"/>
    <alias field="elv1" name="" index="12"/>
    <alias field="HubName" name="" index="13"/>
    <alias field="HubDist" name="" index="14"/>
    <alias field="dist_m" name="" index="15"/>
    <alias field="dBA_dist" name="" index="16"/>
    <alias field="soft_percent" name="" index="17"/>
    <alias field="dBA_src" name="" index="18"/>
    <alias field="dBA_scn" name="" index="19"/>
    <alias field="dBA_reflect" name="" index="20"/>
    <alias field="dur_hr" name="" index="21"/>
    <alias field="op_hr" name="" index="22"/>
    <alias field="dur_percent" name="" index="23"/>
    <alias field="dBA_corrt" name="" index="24"/>
    <alias field="dBA_resultant" name="" index="25"/>
    <alias field="dBA_activity" name="" index="26"/>
  </aliases>
  <defaults>
    <default expression="" field="id" applyOnUpdate="0"/>
    <default expression="" field="left" applyOnUpdate="0"/>
    <default expression="" field="top" applyOnUpdate="0"/>
    <default expression="" field="right" applyOnUpdate="0"/>
    <default expression="" field="bottom" applyOnUpdate="0"/>
    <default expression="" field="_mean" applyOnUpdate="0"/>
    <default expression="" field="_min" applyOnUpdate="0"/>
    <default expression="" field="_max" applyOnUpdate="0"/>
    <default expression="" field="_minority" applyOnUpdate="0"/>
    <default expression="" field="_majority" applyOnUpdate="0"/>
    <default expression="" field="id_2" applyOnUpdate="0"/>
    <default expression="" field="zone" applyOnUpdate="0"/>
    <default expression="" field="elv1" applyOnUpdate="0"/>
    <default expression="" field="HubName" applyOnUpdate="0"/>
    <default expression="" field="HubDist" applyOnUpdate="0"/>
    <default expression="" field="dist_m" applyOnUpdate="0"/>
    <default expression="" field="dBA_dist" applyOnUpdate="0"/>
    <default expression="" field="soft_percent" applyOnUpdate="0"/>
    <default expression="" field="dBA_src" applyOnUpdate="0"/>
    <default expression="" field="dBA_scn" applyOnUpdate="0"/>
    <default expression="" field="dBA_reflect" applyOnUpdate="0"/>
    <default expression="" field="dur_hr" applyOnUpdate="0"/>
    <default expression="" field="op_hr" applyOnUpdate="0"/>
    <default expression="" field="dur_percent" applyOnUpdate="0"/>
    <default expression="" field="dBA_corrt" applyOnUpdate="0"/>
    <default expression="" field="dBA_resultant" applyOnUpdate="0"/>
    <default expression="" field="dBA_activity" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" constraints="0" field="id" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="left" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="top" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="right" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="bottom" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="_mean" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="_min" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="_max" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="_minority" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="_majority" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="id_2" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="zone" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="elv1" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="HubName" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="HubDist" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dist_m" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_dist" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="soft_percent" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_src" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_scn" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_reflect" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dur_hr" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="op_hr" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dur_percent" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_corrt" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_resultant" notnull_strength="0" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" field="dBA_activity" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="id" desc=""/>
    <constraint exp="" field="left" desc=""/>
    <constraint exp="" field="top" desc=""/>
    <constraint exp="" field="right" desc=""/>
    <constraint exp="" field="bottom" desc=""/>
    <constraint exp="" field="_mean" desc=""/>
    <constraint exp="" field="_min" desc=""/>
    <constraint exp="" field="_max" desc=""/>
    <constraint exp="" field="_minority" desc=""/>
    <constraint exp="" field="_majority" desc=""/>
    <constraint exp="" field="id_2" desc=""/>
    <constraint exp="" field="zone" desc=""/>
    <constraint exp="" field="elv1" desc=""/>
    <constraint exp="" field="HubName" desc=""/>
    <constraint exp="" field="HubDist" desc=""/>
    <constraint exp="" field="dist_m" desc=""/>
    <constraint exp="" field="dBA_dist" desc=""/>
    <constraint exp="" field="soft_percent" desc=""/>
    <constraint exp="" field="dBA_src" desc=""/>
    <constraint exp="" field="dBA_scn" desc=""/>
    <constraint exp="" field="dBA_reflect" desc=""/>
    <constraint exp="" field="dur_hr" desc=""/>
    <constraint exp="" field="op_hr" desc=""/>
    <constraint exp="" field="dur_percent" desc=""/>
    <constraint exp="" field="dBA_corrt" desc=""/>
    <constraint exp="" field="dBA_resultant" desc=""/>
    <constraint exp="" field="dBA_activity" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" hidden="0" name="id"/>
      <column width="-1" type="field" hidden="0" name="left"/>
      <column width="-1" type="field" hidden="0" name="top"/>
      <column width="-1" type="field" hidden="0" name="right"/>
      <column width="-1" type="field" hidden="0" name="bottom"/>
      <column width="-1" type="field" hidden="0" name="_mean"/>
      <column width="-1" type="field" hidden="0" name="_min"/>
      <column width="-1" type="field" hidden="0" name="_max"/>
      <column width="-1" type="field" hidden="0" name="_minority"/>
      <column width="-1" type="field" hidden="0" name="_majority"/>
      <column width="-1" type="field" hidden="0" name="id_2"/>
      <column width="-1" type="field" hidden="0" name="landuse"/>
      <column width="-1" type="field" hidden="0" name="elv1"/>
      <column width="-1" type="field" hidden="0" name="HubName"/>
      <column width="-1" type="field" hidden="0" name="HubDist"/>
      <column width="-1" type="field" hidden="0" name="dist_m"/>
      <column width="-1" type="field" hidden="0" name="dBA_dist"/>
      <column width="-1" type="field" hidden="0" name="dBA_src"/>
      <column width="-1" type="field" hidden="0" name="dBA_scn"/>
      <column width="-1" type="field" hidden="0" name="dBA_reflect"/>
      <column width="-1" type="field" hidden="0" name="dur_hr"/>
      <column width="-1" type="field" hidden="0" name="op_hr"/>
      <column width="-1" type="field" hidden="0" name="dur_percent"/>
      <column width="-1" type="field" hidden="0" name="dBA_corrt"/>
      <column width="-1" type="field" hidden="0" name="dBA_resultant"/>
      <column width="-1" type="field" hidden="0" name="dBA_activity"/>
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
  <editforminitcode><![CDATA[]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable/>
  <labelOnTop/>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"HubName"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
