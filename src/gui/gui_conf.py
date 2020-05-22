from PyQt5 import QtWidgets, Qt, QtCore

from aqt import mw
from aqt.deckconf import DeckConf
from aqt.gui_hooks import deck_conf_did_load_config, deck_conf_will_save_config, deck_conf_did_setup_ui_form

from anki.hooks import wrap

from ..lib.config_types import StraightSetting
from ..lib.config import (
    get_setting, get_default_setting,
    write_setting,
    remove_setting, rename_setting,
)

def get_straight_setting_from_dconf(dconf, name: str = 'temp') -> StraightSetting:
    """Save the option for Straight Reward."""
    f = dconf.form

    result = StraightSetting(
        name,
        f.straightLengthSpinBox.value(),
        f.straightEnableNotificationsCheckBox.isChecked(),
        f.straightBaseEaseSpinBox.value(),
        f.straightStepEaseSpinBox.value(),
        f.straightStartEaseSpinBox.value(),
        f.straightStopEaseSpinBox.value(),
    )

    return result

def setup_reward_tab(dconf) -> None:
    """Add an option tab for Straight Reward at Review section on Deckconf dialog."""
    f = dconf.form

    w = QtWidgets.QWidget()
    f.gridLayout_straight = QtWidgets.QGridLayout()
    f.gridLayout_straight.setColumnStretch(1, 5)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    ##### STRAIGHT LENGTH
    f.straightLengthLabel = QtWidgets.QLabel(w)
    f.straightLengthLabel.setText(_('Begin at straight of length'))
    f.gridLayout_straight.addWidget(f.straightLengthLabel, 1, 0, 1, 1)

    f.straightLengthSpinBox = QtWidgets.QSpinBox(w)
    f.straightLengthSpinBox.setMinimum(0)
    f.straightLengthSpinBox.setMaximum(100)
    f.gridLayout_straight.addWidget(f.straightLengthSpinBox, 1, 1, 1, 2)

    ##### ENABLE NOTIFICATIONS
    f.straightEnableNotificationsLabel = QtWidgets.QLabel(w)
    f.straightEnableNotificationsLabel.setText(_('Enable notifications'))
    f.gridLayout_straight.addWidget(f.straightEnableNotificationsLabel, 2, 0, 1, 1)

    f.straightEnableNotificationsCheckBox = QtWidgets.QCheckBox(w)
    f.gridLayout_straight.addWidget(f.straightEnableNotificationsCheckBox, 2, 1, 1, 2)

    ##### BASE EASE
    f.straightBaseEaseLabel = QtWidgets.QLabel(w)
    f.straightBaseEaseLabel.setText(_('Base ease reward'))
    f.gridLayout_straight.addWidget(f.straightBaseEaseLabel, 3, 0, 1, 1)

    f.straightBaseEaseSpinBox = QtWidgets.QSpinBox(w)
    f.straightBaseEaseSpinBox.setSuffix('%')
    f.straightBaseEaseSpinBox.setMinimum(0)
    f.straightBaseEaseSpinBox.setMaximum(999)
    f.gridLayout_straight.addWidget(f.straightBaseEaseSpinBox, 3, 1, 1, 2)

    ##### STEP EASE
    f.straightStepEaseLabel = QtWidgets.QLabel(w)
    f.straightStepEaseLabel.setText(_('Step ease reward'))
    f.gridLayout_straight.addWidget(f.straightStepEaseLabel, 4, 0, 1, 1)

    f.straightStepEaseSpinBox = QtWidgets.QSpinBox(w)
    f.straightStepEaseSpinBox.setSuffix('%')
    f.straightStepEaseSpinBox.setMinimum(0)
    f.straightStepEaseSpinBox.setMaximum(999)
    f.gridLayout_straight.addWidget(f.straightStepEaseSpinBox, 4, 1, 1, 2)

    ##### START EASE
    f.straightStartEaseLabel = QtWidgets.QLabel(w)
    f.straightStartEaseLabel.setText(_('Start at ease'))
    f.gridLayout_straight.addWidget(f.straightStartEaseLabel, 5, 0, 1, 1)

    f.straightStartEaseSpinBox = QtWidgets.QSpinBox(w)
    f.straightStartEaseSpinBox.setSuffix('%')
    f.straightStartEaseSpinBox.setMinimum(130)
    f.straightStartEaseSpinBox.setMaximum(999)
    f.gridLayout_straight.addWidget(f.straightStartEaseSpinBox, 5, 1, 1, 2)

    ##### STOP EASE
    f.straightStopEaseLabel = QtWidgets.QLabel(w)
    f.straightStopEaseLabel.setText(_('Stop at ease'))
    f.gridLayout_straight.addWidget(f.straightStopEaseLabel, 6, 0, 1, 1)

    f.straightStopEaseSpinBox = QtWidgets.QSpinBox(w)
    f.straightStopEaseSpinBox.setSuffix('%')
    f.straightStopEaseSpinBox.setMinimum(130)
    f.straightStopEaseSpinBox.setMaximum(999)
    f.gridLayout_straight.addWidget(f.straightStopEaseSpinBox, 6, 1, 1, 2)

    ##### VERTICAL SPACER
    verticalSpacer = QtWidgets.QSpacerItem(20, 150, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    f.gridLayout_straight.addItem(verticalSpacer)

    w.setLayout(f.gridLayout_straight)
    f.tabWidget.insertTab(2, w, 'Straight Rewards')

def load_reward_tab_with_setting(dconf, sett: StraightSetting) -> None:
    f = dconf.form

    f.straightLengthSpinBox.setValue(sett.straight_length)
    f.straightEnableNotificationsCheckBox.setChecked(sett.enable_notifications)
    f.straightBaseEaseSpinBox.setValue(sett.base_ease)
    f.straightStepEaseSpinBox.setValue(sett.step_ease)
    f.straightStartEaseSpinBox.setValue(sett.start_ease)
    f.straightStopEaseSpinBox.setValue(sett.stop_ease)

def load_reward_tab(dconf, deck, config) -> None:
    """Get the option for Straight Reward."""
    straight_sett = get_setting(mw.col, config['name'])
    load_reward_tab_with_setting(dconf, straight_sett)

def save_reward_tab(dconf, deck, config) -> None:
    setting = get_straight_setting_from_dconf(dconf, config['name'])
    write_setting(mw.col, setting)

def add_straight_setting(dconf, _old) -> None:
    save_names = {c['name'] for c in mw.col.decks.allConf()}
    previous_setting = get_straight_setting_from_dconf(dconf)

    _old(dconf)

    new_names = {c['name'] for c in mw.col.decks.allConf()}
    the_new_name = new_names.difference(save_names)

    if len(the_new_name) == 1:
        load_reward_tab_with_setting(dconf, previous_setting)

    # otherwise user reused an old name
    # this is considered undefined behavior within this add-on

def update_straight_setting(dconf, _old) -> None:
    save_names = {c['name'] for c in mw.col.decks.allConf()}

    _old(dconf)

    new_names = {c['name'] for c in mw.col.decks.allConf()}
    name_for_deletion = save_names.difference(new_names)

    if len(name_for_deletion) == 1:
        remove_setting(mw.col, name_for_deletion.pop())

    # otherwise user renamed conf to old name, or reuses name
    # reusing a name is considered undefined behavior within this add-on

def init_conf():
    deck_conf_did_setup_ui_form.append(setup_reward_tab)
    deck_conf_did_load_config.append(load_reward_tab)
    deck_conf_will_save_config.append(save_reward_tab)

    DeckConf.addGroup = wrap(DeckConf.addGroup, add_straight_setting, 'around')
    DeckConf.remGroup = wrap(DeckConf.remGroup, update_straight_setting, 'around')
    DeckConf.renameGroup = wrap(DeckConf.renameGroup, update_straight_setting, 'around')
