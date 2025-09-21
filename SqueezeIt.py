import bpy
import os

bl_info = {
    "name": "SQUEEZE IT",
    "author": "Kiana Eyvani",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Adjust Quality",
    "description": "Professional-grade texture resolution control to support high-performance Blender workflows.",
    "category": "3D View",
}


class AdjustImageQualityPanel(bpy.types.Panel):
    bl_label = "Adjust Image Quality"
    bl_idname = "VIEW3D_PT_adjust_quality"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Squeeze It'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.adjust_quality_props

        # Save Path
        box = layout.box()
        box.label(text="Save Settings", icon="FILE_FOLDER")
        box.prop(props, "save_path", text="Save Path")
        box.operator("object.set_save_path", text="Set Save Path", icon="FILE_TICK")

        # Apply Quality Panel
        box = layout.box()
        box.label(text="Apply Quality", icon="IMAGE_DATA")
        box.prop(props, "quality", text="Select Quality")
        if props.quality == 'CUSTOM':
            box.prop(props, "custom_quality", text="Custom Resolution")

        box.operator("object.apply_quality_all", text="Apply to All Photos", icon="IMAGE_DATA")
        box.operator("object.apply_quality_selected", text="Apply to Selected Photo", icon="IMAGE")

        # Undo Panel
        box = layout.box()
        box.label(text="Undo / Restore", icon="LOOP_BACK")
        box.operator("object.restore_original_image", text="Restore Selected Image", icon="FILE_REFRESH")
        box.operator("object.restore_all_originals", text="Restore All Originals", icon="FILE_REFRESH")

        # Distance-Based Quality Panel
        box = layout.box()
        box.label(text="Quality by Distance", icon="DRIVER_DISTANCE")
        box.operator("object.detect_nearest_farthest", text="Detect Nearest & Farthest", icon="VIEW_CAMERA")
        box.label(text=f"Nearest: {scene.quality_by_distance_props.nearest_image}")
        box.label(text=f"Farthest: {scene.quality_by_distance_props.farthest_image}")
        box.prop(scene.quality_by_distance_props, "nearest_quality", text="Nearest Quality")
        if scene.quality_by_distance_props.nearest_quality == 'CUSTOM':
            box.prop(scene.quality_by_distance_props, "nearest_custom_quality", text="Custom Nearest Quality")
        box.prop(scene.quality_by_distance_props, "farthest_quality", text="Farthest Quality")
        if scene.quality_by_distance_props.farthest_quality == 'CUSTOM':
            box.prop(scene.quality_by_distance_props, "farthest_custom_quality", text="Custom Farthest Quality")
        box.prop(scene.quality_by_distance_props, "min_distance", text="Min Distance")
        box.prop(scene.quality_by_distance_props, "max_distance", text="Max Distance")
        box.operator("object.apply_quality_by_distance", text="Apply Quality by Distance", icon="IMAGE_DATA")


class AdjustImageQualityProperties(bpy.types.PropertyGroup):
    save_path: bpy.props.StringProperty(
        name="Save Path",
        description="Directory where images will be saved",
        default=""
    )
    quality: bpy.props.EnumProperty(
        name="Quality",
        description="Select resolution for images",
        items=[
            ('4096', "4096x4096", ""),
            ('2048', "2048x2048", ""),
            ('1024', "1024x1024", ""),
            ('512', "512x512", ""),
            ('128', "128x128", ""),
            ('CUSTOM', "Custom", "")
        ],
        default='4096'
    )
    custom_quality: bpy.props.IntProperty(
        name="Custom Quality",
        description="Custom resolution for images",
        default=1024,
        min=1
    )


class QualityByDistanceProperties(bpy.types.PropertyGroup):
    nearest_image: bpy.props.StringProperty(name="Nearest Image", default="")
    farthest_image: bpy.props.StringProperty(name="Farthest Image", default="")

    nearest_quality: bpy.props.EnumProperty(
        name="Nearest Quality",
        description="Resolution for the nearest image",
        items=[
            ('4096', "4096x4096", ""),
            ('2048', "2048x2048", ""),
            ('1024', "1024x1024", ""),
            ('512', "512x512", ""),
            ('128', "128x128", ""),
            ('CUSTOM', "Custom", "")
        ],
        default='4096'
    )
    nearest_custom_quality: bpy.props.IntProperty(
        name="Custom Nearest Quality",
        description="Custom resolution for nearest image",
        default=1024,
        min=1
    )

    farthest_quality: bpy.props.EnumProperty(
        name="Farthest Quality",
        description="Resolution for the farthest image",
        items=[
            ('4096', "4096x4096", ""),
            ('2048', "2048x2048", ""),
            ('1024', "1024x1024", ""),
            ('512', "512x512", ""),
            ('128', "128x128", ""),
            ('CUSTOM', "Custom", "")
        ],
        default='512'
    )
    farthest_custom_quality: bpy.props.IntProperty(
        name="Custom Farthest Quality",
        description="Custom resolution for farthest image",
        default=512,
        min=1
    )

    min_distance: bpy.props.FloatProperty(
        name="Minimum Distance",
        description="Start of quality gradient (closest)",
        default=0.0,
        min=0.0
    )

    max_distance: bpy.props.FloatProperty(
        name="Maximum Distance",
        description="End of quality gradient (farthest)",
        default=10.0,
        min=0.01
    )


class SetSavePathOperator(bpy.types.Operator):
    bl_idname = "object.set_save_path"
    bl_label = "Set Save Path"
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")
    bl_description = "Open a file browser to choose the folder where images will be saved"

    def execute(self, context):
        context.scene.adjust_quality_props.save_path = self.filepath
        self.report({'INFO'}, f"Save path set to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class ApplyQualityAllOperator(bpy.types.Operator):
    bl_idname = "object.apply_quality_all"
    bl_label = "Apply Quality to All Photos"
    bl_description = "Apply the selected resolution to all images in the scene"

    def execute(self, context):
        adjust_image_quality(context, apply_to_all=True)
        return {'FINISHED'}
    



class ApplyQualitySelectedOperator(bpy.types.Operator):
    bl_idname = "object.apply_quality_selected"
    bl_label = "Apply Quality to Selected Photo"
    bl_description = "Apply the selected resolution only to the currently selected object in the scene"

    def execute(self, context):
        adjust_image_quality(context, apply_to_all=False)
        return {'FINISHED'}
    



class RestoreOriginalImageOperator(bpy.types.Operator):
    bl_idname = "object.restore_original_image"
    bl_label = "Restore Original Image"
    bl_description = "Restore the original resolution of the selected image, if a backup exists"

    def execute(self, context):
        scene = context.scene
        props = scene.adjust_quality_props
        save_path = props.save_path

        if not save_path:
            self.report({'WARNING'}, "No save path set.")
            return {'CANCELLED'}

        img = context.object.active_material.node_tree.nodes["Image Texture"].image
        if not img:
            self.report({'WARNING'}, "No image found.")
            return {'CANCELLED'}

        original_path = os.path.join(save_path, f"{img.name}_original.png")
        if os.path.exists(original_path):
            img_file = bpy.data.images.load(original_path)
            img_file.colorspace_settings.name = 'sRGB'
            context.object.active_material.node_tree.nodes["Image Texture"].image = img_file
            self.report({'INFO'}, f"Restored original image from {original_path}")
        else:
            self.report({'WARNING'}, f"No original image found at {original_path}")
        return {'FINISHED'}
    
        


class RestoreAllOriginalsOperator(bpy.types.Operator):
    bl_idname = "object.restore_all_originals"
    bl_label = "Restore All Original Images"
    bl_description = "Restore all images to their original resolution from backups"

    def execute(self, context):
        scene = context.scene
        props = scene.adjust_quality_props
        save_path = props.save_path

        if not save_path:
            self.report({'WARNING'}, "No save path set.")
            return {'CANCELLED'}

        restored_count = 0
        for img in bpy.data.images:
            original_path = os.path.join(save_path, f"{img.name}_original.png")
            if os.path.exists(original_path):
                try:
                    restored_img = bpy.data.images.load(original_path)
                    restored_img.colorspace_settings.name = 'sRGB'
                    img.filepath = restored_img.filepath
                    img.reload()
                    restored_count += 1
                except:
                    self.report({'WARNING'}, f"Could not restore: {img.name}")
        if restored_count == 0:
            self.report({'WARNING'}, "No original images found.")
        else:
            self.report({'INFO'}, f"Restored {restored_count} original images.")
        return {'FINISHED'}
    
        


class DetectNearestFarthestOperator(bpy.types.Operator):
    bl_idname = "object.detect_nearest_farthest"
    bl_label = "Detect Nearest & Farthest Images"
    bl_description = "Detect the nearest and farthest images relative to the active camera in the scene"

    def execute(self, context):
        scene = context.scene
        props = scene.quality_by_distance_props
        camera = scene.camera

        if not camera:
            self.report({'WARNING'}, "No active camera found")
            return {'CANCELLED'}

        images = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.active_material:
                nodes = obj.active_material.node_tree.nodes
                if "Image Texture" in nodes:
                    img = nodes["Image Texture"].image
                    if img:
                        dist = (camera.location - obj.location).length
                        images.append((dist, img))

        if not images:
            self.report({'WARNING'}, "No images found")
            return {'CANCELLED'}

        images.sort(key=lambda x: x[0])
        props.nearest_image = images[0][1].name
        props.farthest_image = images[-1][1].name
        return {'FINISHED'}
    
        


class ApplyQualityByDistanceOperator(bpy.types.Operator):
    bl_idname = "object.apply_quality_by_distance"
    bl_label = "Apply Quality Based on Distance"
    bl_description = "Apply quality settings to images based on their distance from the camera. Nearest images get higher quality."

    def execute(self, context):
        scene = context.scene
        props = scene.quality_by_distance_props
        save_props = scene.adjust_quality_props
        save_path = save_props.save_path
        camera = scene.camera

        if not camera:
            self.report({'WARNING'}, "No active camera found")
            return {'CANCELLED'}

        images = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.active_material:
                nodes = obj.active_material.node_tree.nodes
                if "Image Texture" in nodes:
                    img = nodes["Image Texture"].image
                    if img:
                        dist = (camera.location - obj.location).length
                        images.append((dist, img))

        if not images:
            self.report({'WARNING'}, "No images found")
            return {'CANCELLED'}

        if not save_path:
            self.report({'WARNING'}, "No save path set.")
            return {'CANCELLED'}
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        min_dist = props.min_distance
        max_dist = props.max_distance
        if min_dist >= max_dist:
            self.report({'WARNING'}, "Min Distance must be less than Max Distance.")
            return {'CANCELLED'}

        nearest_q = int(props.nearest_custom_quality) if props.nearest_quality == 'CUSTOM' else int(props.nearest_quality)
        farthest_q = int(props.farthest_custom_quality) if props.farthest_quality == 'CUSTOM' else int(props.farthest_quality)

        for dist, img in images:
            original_path = os.path.join(save_path, f"{img.name}_original.png")
            if not os.path.exists(original_path):
                try:
                    img.save_render(original_path)
                except:
                    self.report({'WARNING'}, f"Could not save original for {img.name}")

            factor = (dist - min_dist) / (max_dist - min_dist)
            factor = max(0.0, min(1.0, factor))
            new_quality = int(nearest_q + factor * (farthest_q - nearest_q))
            img.scale(new_quality, new_quality)
            self.report({'INFO'}, f"Set {img.name} to {new_quality}x{new_quality}")

        return {'FINISHED'}
    
        


def adjust_image_quality(context, apply_to_all):
    scene = context.scene
    props = scene.adjust_quality_props
    save_path = props.save_path

    if not save_path:
        print("No save path set.")
        return

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    images = bpy.data.images if apply_to_all else [context.object.active_material.node_tree.nodes["Image Texture"].image]

    for img in images:
        if img.source != 'FILE':
            continue

        new_quality = int(props.custom_quality) if props.quality == 'CUSTOM' else int(props.quality)

        original_path = os.path.join(save_path, f"{img.name}_original.png")
        if not os.path.exists(original_path):
            try:
                img.save_render(original_path)
            except:
                print(f"Could not save original image: {img.name}")

        try:
            img.scale(new_quality, new_quality)
            img_path = os.path.join(save_path, f"{img.name}_quality_{new_quality}.png")
            img.save_render(img_path)
        except:
            print(f"Could not scale/save image: {img.name}")


def register():
    for cls in [
        AdjustImageQualityPanel, AdjustImageQualityProperties, SetSavePathOperator,
        ApplyQualityAllOperator, ApplyQualitySelectedOperator, RestoreOriginalImageOperator,
        DetectNearestFarthestOperator, ApplyQualityByDistanceOperator,
        QualityByDistanceProperties, RestoreAllOriginalsOperator
    ]:
        bpy.utils.register_class(cls)
    bpy.types.Scene.adjust_quality_props = bpy.props.PointerProperty(type=AdjustImageQualityProperties)
    bpy.types.Scene.quality_by_distance_props = bpy.props.PointerProperty(type=QualityByDistanceProperties)


def unregister():
    for cls in reversed([
        AdjustImageQualityPanel, AdjustImageQualityProperties, SetSavePathOperator,
        ApplyQualityAllOperator, ApplyQualitySelectedOperator, RestoreOriginalImageOperator,
        DetectNearestFarthestOperator, ApplyQualityByDistanceOperator,
        QualityByDistanceProperties, RestoreAllOriginalsOperator
    ]):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.adjust_quality_props
    del bpy.types.Scene.quality_by_distance_props


if __name__ == "__main__":
    register()


