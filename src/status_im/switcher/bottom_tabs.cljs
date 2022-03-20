(ns status-im.switcher.bottom-tabs
  (:require [quo.react-native :as rn]
            [reagent.core :as reagent]
            [status-im.switcher.styles :as styles]
            [status-im.utils.handlers :refer [>evt]]
            [status-im.ui.components.icons.icons :as icons]))

(def selected-tab-id (reagent/atom :chats-stack))

(defn bottom-tab-pressed [tab-id]
  (when-not (= tab-id @selected-tab-id)
    (reset! selected-tab-id tab-id)
    (>evt [:navigate-change-tab-nav2 tab-id])))

;; TODO(parvesh) - reimplement tab with counter, once design is complete
(defn bottom-tab [icon tab-id]
  [rn/touchable-opacity {:style          {:padding 15}
                         :active-opacity 1
                         :on-press       #(bottom-tab-pressed tab-id)}
   [icons/icon icon (styles/bottom-tab-icon
                     (if (= tab-id @selected-tab-id)
                       :bottom-tabs-selected-tab
                       :bottom-tabs-non-selected-tab))]])

(defn bottom-tabs []
  [rn/animated-view {:style (styles/bottom-tabs)}
   [bottom-tab :main-icons/messages-new :chats-stack]
   [bottom-tab :main-icons/communities :communities-stack]
   [rn/view {:width 10}]
   [bottom-tab :main-icons/wallet-new :wallet-stack]
   [bottom-tab :main-icons/browser :browser-stack]])
