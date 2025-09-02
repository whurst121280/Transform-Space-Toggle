bl_info = {
    "name": "Transform Space Toggle",
    "author": "Two turn tables and an LLM",
    "version": (2, 1, 5),
    "blender": (4, 5, 0),
    "location": "View3D",
    "description": "Cycle through user-defined Transform Spaces with a single hotkey (keyboard or mouse, incl. double-click).",
    "category": "3D View",
}

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    IntProperty,
)

addon_keymaps = []

VALID_TYPES = (
    ('GLOBAL',  "GLOBAL",  "World-aligned orientation"),
    ('LOCAL',   "LOCAL",   "Object local orientation"),
    ('VIEW',    "VIEW",    "View-aligned orientation"),
    ('NORMAL',  "NORMAL",  "Normal-based orientation"),
    ('GIMBAL',  "GIMBAL",  "Gimbal orientation"),
    ('PARENT',  "PARENT",  "Parent orientation"),
    ('CURSOR',  "CURSOR",  "3D Cursor orientation"),
)

# For hotkey input
# For hotkey input (reader-friendly labels)
KEY_TYPES = [
    # Letters
    *[(c, c, "") for c in (
        'A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
    )],

    # Function keys
    *[(f"F{i}", f"F{i}", "") for i in range(1, 12 + 1)],

    # Digits (show 1–0 instead of ONE…ZERO)
    ('ONE',   '1',  ''),
    ('TWO',   '2',  ''),
    ('THREE', '3',  ''),
    ('FOUR',  '4',  ''),
    ('FIVE',  '5',  ''),
    ('SIX',   '6',  ''),
    ('SEVEN', '7',  ''),
    ('EIGHT', '8',  ''),
    ('NINE',  '9',  ''),
    ('ZERO',  '0',  ''),

    # Mouse (friendlier names)
    ('LEFTMOUSE',    'Left Mouse',    'Left mouse button'),
    ('MIDDLEMOUSE',  'Middle Mouse',  'Middle mouse button'),
    ('RIGHTMOUSE',   'Right Mouse',   'Right mouse button'),
    ('BUTTON4MOUSE', 'Mouse Button 4','Side button 1'),
    ('BUTTON5MOUSE', 'Mouse Button 5','Side button 2'),
    ('WHEELUPMOUSE',   'Wheel Up',    'Scroll wheel up'),
    ('WHEELDOWNMOUSE', 'Wheel Down',  'Scroll wheel down'),
]

# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------

class TRANSFORM_OT_cycle_space(bpy.types.Operator):
    """Cycle transform orientation through the user-defined list"""
    bl_idname = "transform.cycle_space"
    bl_label = "Cycle Transform Space"
    bl_description = "Cycle through the Transform Spaces defined in Add-on Preferences"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        spaces = [item.space for item in prefs.spaces]
        if not spaces:
            self.report({'WARNING'}, "No Transform Spaces configured. Add some in Preferences > Add-ons.")
            return {'CANCELLED'}

        slot = context.scene.transform_orientation_slots[0]
        current = slot.type

        # If current not in list, jump to first. Else advance.
        try:
            idx = spaces.index(current)
            idx = (idx + 1) % len(spaces)
        except ValueError:
            idx = 0

        new_type = spaces[idx]
        try:
            slot.type = new_type
        except Exception:
            self.report({'WARNING'}, f"Failed to set transform orientation to {new_type}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Transform Orientation: {slot.type}")
        return {'FINISHED'}


# Legacy toggle kept for compatibility (not used by the new keymap)
class TRANSFORM_OT_toggle_space(bpy.types.Operator):
    bl_idname = "transform.toggle_space"
    bl_label = "Toggle Transform Space (Legacy)"
    bl_description = "Legacy: Toggle between Local and Global"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        slot = context.scene.transform_orientation_slots[0]
        slot.type = "GLOBAL" if slot.type == "LOCAL" else "LOCAL"
        self.report({"INFO"}, f"Transform Orientation set to {slot.type}")
        return {"FINISHED"}


# -----------------------------------------------------------------------------
# Preferences (global hotkey + cycle list UI)
# -----------------------------------------------------------------------------

class TST_BindingSpace(bpy.types.PropertyGroup):
    space: EnumProperty(
        name="Space",
        description="Transform Space to include in cycle list",
        items=VALID_TYPES,
        default='GLOBAL',
    )

class TRANSFORM_SPACE_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Global hotkey (same for all spaces)
    key_type: EnumProperty(
        name="Key/Mouse",
        description="Choose the event type for the hotkey (supports mouse)",
        items=KEY_TYPES,
        default='Q',
    )
    event_value: EnumProperty(
        name="Action",
        description="Press or Double Click",
        items=[
            ('PRESS', "Press", "Activate on press/click"),
            ('DOUBLE_CLICK', "Double Click", "Activate on double click"),
        ],
        default='PRESS',
    )
    use_ctrl: BoolProperty(name="Ctrl", default=True)
    use_shift: BoolProperty(name="Shift", default=True)
    use_alt: BoolProperty(name="Alt", default=False)

    # Cycle list
    spaces: CollectionProperty(type=TST_BindingSpace)
    spaces_index: IntProperty(default=0)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        # -------------------- Hotkey --------------------
        box = layout.box()
        box.label(text="Hotkey")
        row = box.row(align=True)
        c1 = row.column(align=True); c1.ui_units_x = 9
        c1.prop(self, "key_type", text="")
        sp = row.column(align=True); sp.ui_units_x = 1; sp.label(text="")
        c2 = row.column(align=True); c2.ui_units_x = 8
        c2.prop(self, "event_value", text="")
        mods = box.row(align=True)
        mods.prop(self, "use_ctrl"); mods.prop(self, "use_shift"); mods.prop(self, "use_alt")
        
        # Add Hotkey button directly under hotkey fields
        box.operator("transform_space.apply_hotkey", icon='CHECKMARK', text="Add Hotkey")
        box.label(text="Hotkey is Applied in Blenders Keymap.")
        box.label(text= "It can be found under ''Keymap > 3D View > Cycle Transform Space'' ")
        # -------------------- Transform Spaces --------------------
        box = layout.box()
        header = box.row(align=True)
        header.label(text="Transform Spaces")
        header.operator("transform_space.add_space", text="", icon="ADD")
        header.operator("transform_space.remove_space", text="", icon="REMOVE")
        header.separator()
        header.operator("transform_space.move_space_up", text="", icon="TRIA_UP")
        header.operator("transform_space.move_space_down", text="", icon="TRIA_DOWN")

        # List display
        row = box.row()
        row.template_list("TST_UL_spaces", "", self, "spaces", self, "spaces_index", rows=5)

        # Selected item view
        if 0 <= self.spaces_index < len(self.spaces):
            item = self.spaces[self.spaces_index]
            sub = box.row(align=True)
            sub.label(text=f"Selected: {item.space}")

        # Warning if empty
        if not self.spaces:
            warn = box.row()
            warn.label(text="No spaces configured. Add at least one.", icon='ERROR')

class TST_UL_spaces(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"{index+1}. {item.space}")


# -----------------------------------------------------------------------------
# Keymap helpers and Apply operator
# -----------------------------------------------------------------------------

def clear_addon_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()

def apply_hotkey_from_prefs(prefs):
    _ensure_default_spaces(prefs)
    clear_addon_keymaps()
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(
        "transform.cycle_space",
        type=prefs.key_type,
        value=prefs.event_value,
        ctrl=prefs.use_ctrl,
        shift=prefs.use_shift,
        alt=prefs.use_alt,
    )
    addon_keymaps.append((km, kmi))

class TRANSFORM_SPACE_OT_apply_hotkey(bpy.types.Operator):
    bl_idname = "transform_space.apply_hotkey"
    bl_label = "Apply/Add Hotkey"
    bl_description = "Register or update the Transform Space Toggle hotkey under Keymap > Add-ons"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        apply_hotkey_from_prefs(prefs)
        self.report({'INFO'}, "Transform Space Toggle: hotkey added/updated")
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Space list operators
# -----------------------------------------------------------------------------

def _ensure_default_spaces(prefs):
    if not prefs.spaces:
        item = prefs.spaces.add(); item.space = 'GLOBAL'
        item = prefs.spaces.add(); item.space = 'LOCAL'
        prefs.spaces_index = max(0, len(prefs.spaces)-1)

def _current_space_keys(prefs):
    return [i.space for i in prefs.spaces]

class TST_OT_add_space(bpy.types.Operator):
    bl_idname = "transform_space.add_space"
    bl_label = "Add Transform Space"
    bl_description = "Add a new Transform Space to the cycle list"

    # Let the user pick exactly which space to add (dialog)
    space_choice: EnumProperty(
        name="Transform Space",
        items=VALID_TYPES,
        default='GLOBAL',
    )

    def invoke(self, context, event):
        # Pre-select the first missing one to reduce clicks
        prefs = context.preferences.addons[__name__].preferences
        existing = _current_space_keys(prefs)
        for key, _l, _d in VALID_TYPES:
            if key not in existing:
                self.space_choice = key
                break
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "space_choice", text="")

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        existing = _current_space_keys(prefs)
        if self.space_choice in existing:
            self.report({'INFO'}, f"{self.space_choice} is already in the list.")
            return {'CANCELLED'}
        item = prefs.spaces.add()
        item.space = self.space_choice
        prefs.spaces_index = len(prefs.spaces)-1
        return {'FINISHED'}

class TST_OT_remove_space(bpy.types.Operator):
    bl_idname = "transform_space.remove_space"
    bl_label = "Remove Transform Space"
    bl_description = "Remove the selected Transform Space from the cycle list"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.spaces_index
        if 0 <= idx < len(prefs.spaces):
            prefs.spaces.remove(idx)
            prefs.spaces_index = min(idx, len(prefs.spaces)-1)
        return {'FINISHED'}

class TST_OT_move_space_up(bpy.types.Operator):
    bl_idname = "transform_space.move_space_up"
    bl_label = "Move Up"
    bl_description = "Move the selected Transform Space up"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.spaces_index
        if 0 < idx < len(prefs.spaces):
            prefs.spaces.move(idx, idx-1)
            prefs.spaces_index = idx-1
        return {'FINISHED'}

class TST_OT_move_space_down(bpy.types.Operator):
    bl_idname = "transform_space.move_space_down"
    bl_label = "Move Down"
    bl_description = "Move the selected Transform Space down"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.spaces_index
        if 0 <= idx < len(prefs.spaces)-1:
            prefs.spaces.move(idx, idx+1)
            prefs.spaces_index = idx+1
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Register / Unregister
# -----------------------------------------------------------------------------

classes = (
    TRANSFORM_OT_cycle_space,
    TRANSFORM_OT_toggle_space,  # legacy
    TST_BindingSpace,
    TRANSFORM_SPACE_Preferences,
    TST_UL_spaces,
    TRANSFORM_SPACE_OT_apply_hotkey,
    TST_OT_add_space,
    TST_OT_remove_space,
    TST_OT_move_space_up,
    TST_OT_move_space_down,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = bpy.context.preferences.addons[__name__].preferences
    _ensure_default_spaces(prefs)
    apply_hotkey_from_prefs(prefs)

def unregister():
    clear_addon_keymaps()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

if __name__ == "__main__":
    register()
