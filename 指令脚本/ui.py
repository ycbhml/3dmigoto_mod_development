import bpy
import addon_utils
from bl_ui.generic_ui_list import draw_ui_list
from .operators import ClearSemanticRemapList, PrefillSemanticRemapList, Import3DMigotoFrameAnalysis, Import3DMigotoRaw, Import3DMigotoPose, Export3DMigoto, ApplyVGMap, Export3DMigotoXXMI

class MIGOTO_UL_semantic_remap_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "semantic_from", text="", emboss=False, icon_value=icon)
            if item.InputSlotClass == 'per-instance':
                layout.label(text="实例数据")
                layout.enabled = False
            elif item.valid == False:
                layout.label(text="无效")
                layout.enabled = False
            else:
                layout.prop(item, "semantic_to", text="", emboss=False, icon_value=icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class MIGOTO_MT_semantic_remap_menu(bpy.types.Menu):
    bl_label = "语义重映射选项"

    def draw(self, context):
        layout = self.layout
        layout.operator(ClearSemanticRemapList.bl_idname)
        layout.operator(PrefillSemanticRemapList.bl_idname)

class MigotoImportOptionsPanelBase(object):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        operator = context.space_data.active_operator
        return operator.bl_idname == "IMPORT_MESH_OT_migoto_frame_analysis"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

class MIGOTO_PT_ImportFrameAnalysisMainPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 0

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "flip_texcoord_v")
        self.layout.prop(operator, "flip_winding")
        self.layout.prop(operator, "flip_normal")

class MIGOTO_PT_ImportFrameAnalysisRelatedFilesPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 1

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.enabled = not operator.load_buf
        self.layout.prop(operator, "load_related")
        self.layout.prop(operator, "load_related_so_vb")
        self.layout.prop(operator, "merge_meshes")

class MIGOTO_PT_ImportFrameAnalysisBufFilesPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "改为加载 .buf 文件"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw_header(self, context):
        operator = context.space_data.active_operator
        self.layout.prop(operator, "load_buf", text="")

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.enabled = operator.load_buf
        self.layout.prop(operator, "load_buf_limit_range")

class MIGOTO_PT_ImportFrameAnalysisBonePanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw_header(self, context):
        operator = context.space_data.active_operator
        self.layout.prop(operator, "pose_cb")

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "pose_cb_off")
        self.layout.prop(operator, "pose_cb_step")

class MIGOTO_PT_ImportFrameAnalysisRemapSemanticsPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "语义重映射"
    bl_order = 4

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        draw_ui_list(self.layout, context,
                class_name='MIGOTO_UL_semantic_remap_list',
                menu_class_name='MIGOTO_MT_semantic_remap_menu',
                list_path='active_operator.properties.semantic_remap',
                active_index_path='active_operator.properties.semantic_remap_idx',
                unique_id='migoto_import_semantic_remap_list',
                item_dyntip_propname='tooltip',
                )

class MIGOTO_PT_ImportFrameAnalysisManualOrientation(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "方向"
    bl_order = 5

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "axis_forward")
        self.layout.prop(operator, "axis_up")

class MIGOTO_PT_ImportFrameAnalysisCleanUp(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "导入后清理网格"
    bl_order = 6

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "merge_verts")
        self.layout.prop(operator, "tris_to_quads")
        self.layout.prop(operator, "clean_loose")

class XXMI_PT_Sidebar(bpy.types.Panel):
    '''主面板'''
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "XXMI 工具"
    bl_idname = "XXMI_PT_Sidebar"
    bl_label = "XXMI 工具"
    bl_context = "objectmode"

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        version = ""
        for module in addon_utils.modules():
            if module.bl_info.get('name') == "XXMI 工具":
                version = module.bl_info.get('version', (-1, -1, -1))
                break
        version = ".".join(str(i) for i in version)
        row.alignment = 'RIGHT'
        row.label(text="版本 "+version)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        xxmi = context.scene.xxmi
        split = layout.split(factor=0.85)
        col_1 = split.column()
        col_2 = split.column()
        col_1.prop(xxmi, "dump_path", text="转储路径")
        col_1.prop(xxmi, "destination_path", text="目标路径")
        col_2.operator("dump.selector", icon="FILE_FOLDER", text="")
        col_2.operator("destination.selector", icon="FILE_FOLDER", text="")
        layout.separator()
        col = layout.column(align=True)
        col.prop(xxmi, 'game')

class XXMISidebarOptionsPanelBase(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "XXMI_PT_Sidebar"

    def draw(self, context):
        self.layout.use_property_split = False
        self.layout.use_property_decorate = False

class XXMI_PT_SidePanelExportSettings(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = "导出设置"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        box = self.layout.box()
        row = box.row()
        col = row.column(align=True)
        col.prop(xxmi, 'flip_winding', text="翻转绕组")
        col.prop(xxmi, 'flip_normal', text="翻转法线")
        col.prop(xxmi, 'use_foldername', text="导出时使用文件夹名")
        col.prop(xxmi, 'ignore_hidden', text="忽略隐藏对象")
        col.prop(xxmi, 'only_selected', text="仅导出选中对象")
        col.prop(xxmi, 'no_ramps', text="忽略渐变阴影/金属贴图/漫反射指南")
        col.prop(xxmi, 'delete_intermediate', text="删除中间文件")
        col.prop(xxmi, 'copy_textures', text="复制纹理")
        col.prop(xxmi, 'apply_modifiers_and_shapekeys', text="应用修改器和形状键")
        col.prop(xxmi, 'normalize_weights', text="规范化权重")

class XXMI_PT_SidePanelExportCredit(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 2

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        col = self.layout.column(align=True)
        col.prop(xxmi, 'credit', text="制作人员")

class XXMI_PT_SidePanelOutline(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    def draw_header(self, context):
        xxmi = context.scene.xxmi
        self.layout.prop(xxmi, "outline_optimization", text="启用轮廓优化")

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        self.layout.enabled = xxmi.outline_optimization
        box = self.layout.box()
        row = box.row()
        col = row.column(align=True)
        
        col.prop(xxmi, "toggle_rounding_outline", text='顶点位置四舍五入', toggle=True, icon="SHADING_WIRE")
        col.prop(xxmi, "decimal_rounding_outline", text="小数点位数")
        if xxmi.toggle_rounding_outline:
            col.prop(xxmi, "detect_edges", text="检测边缘")
        if xxmi.detect_edges and xxmi.toggle_rounding_outline:
            col.prop(xxmi, "nearest_edge_distance", text="最近边缘距离")
        col.prop(xxmi, "overlapping_faces", text="忽略重叠面")
        col.prop(xxmi, "angle_weighted", text="角度加权")
        col.prop(xxmi, "calculate_all_faces", text="计算所有面")

class XXMI_PT_SidePanelExport(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 99

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        layout = self.layout
        row = layout.row()
        row.operator("xxmi.exportadvanced", text="导出模组")

def menu_func_import_fa(self, context):
    self.layout.operator(Import3DMigotoFrameAnalysis.bl_idname, text="3DMigoto 框架分析转储 (vb.txt + ib.txt)")

def menu_func_import_raw(self, context):
    self.layout.operator(Import3DMigotoRaw.bl_idname, text="3DMigoto 原始缓冲区 (.vb + .ib)")

def menu_func_import_pose(self, context):
    self.layout.operator(Import3DMigotoPose.bl_idname, text="3DMigoto 姿势 (.txt)")

def menu_func_export(self, context):
    self.layout.operator(Export3DMigoto.bl_idname, text="3DMigoto 原始缓冲区 (.vb + .ib)")

def menu_func_export_xxmi(self, context):
    self.layout.operator(Export3DMigotoXXMI.bl_idname, text="导出模组文件夹")

def menu_func_apply_vgmap(self, context):
    self.layout.operator(ApplyVGMap.bl_idname, text="将 3DMigoto 顶点组映射应用到当前对象 (.vgmap)")

import_menu = bpy.types.TOPBAR_MT_file_import
export_menu = bpy.types.TOPBAR_MT_file_export

def register():
    import_menu.append(menu_func_import_fa)
    import_menu.append(menu_func_import_raw)
    export_menu.append(menu_func_export)
    export_menu.append(menu_func_export_xxmi)
    import_menu.append(menu_func_apply_vgmap)
    import_menu.append(menu_func_import_pose)

def unregister():
    import_menu.remove(menu_func_import_fa)
    import_menu.remove(menu_func_import_raw)
    export_menu.remove(menu_func_export)
    export_menu.remove(menu_func_export_xxmi)
    import_menu.remove(menu_func_apply_vgmap)
    import_menu.remove(menu_func_import_pose)
