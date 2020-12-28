(ns status-im.ui.screens.multiaccounts.sheets
  (:require [quo.core :as quo]
            [status-im.i18n :as i18n]
            [status-im.ui.components.react :as react]
            [re-frame.core :as re-frame]))

(defn actions-sheet []
  [react/view
   [quo/list-item {:theme               :accent
                   :on-press            #(do (re-frame/dispatch [:bottom-sheet/hide])
                                             (re-frame/dispatch [:multiaccounts.create.ui/intro-wizard]))
                   :icon                :main-icons/add
                   :accessibility-label :generate-a-new-key
                   :title               (i18n/label :t/generate-a-new-key)}]])

(defn database-management-sheet [on-backup on-import on-export]
  (fn []
    [react/view
     [quo/list-item {:theme               :accent
                     :on-press            #(do (re-frame/dispatch [:bottom-sheet/hide])
                                               (on-backup))
                     :icon                :main-icons/copy
                     :title               "Backup encrypted"}]
     [quo/list-item {:theme               :accent
                     :on-press            #(do (re-frame/dispatch [:bottom-sheet/hide])
                                               (on-import))
                     :icon                :main-icons/receive
                     :title               "Import unencrypted"}]
     [quo/list-item {:theme               :accent
                     :on-press            #(do (re-frame/dispatch [:bottom-sheet/hide])
                                               (on-export))
                     :icon                :main-icons/send
                     :title               "Export unencrypted"}]]))
