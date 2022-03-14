(ns status-im.ui.screens.wallet.accounts.common
  (:require [quo.core :as quo]
            [status-im.wallet.utils :as wallet.utils]
            [status-im.ui.screens.wallet.components.views :as wallet.components]
            [status-im.ui.components.chat-icon.screen :as chat-icon]
            [reagent.core :as reagent]
            [quo.react-native :as rn]
            [status-im.utils.utils :as utils.utils]
            [re-frame.core :as re-frame]))

;; Note(rasom): sometimes `refreshing` might get stuck on iOS if action happened
;; too fast. By updating this atom in 1s we ensure that `refreshing?` property
;; is updated properly in this case.
(def updates-counter (reagent/atom 0))

(defn schedule-counter-reset []
  (utils.utils/set-timeout
   (fn []
     (swap! updates-counter inc)
     (when @(re-frame/subscribe [:wallet/refreshing-history?])
       (schedule-counter-reset)))
   1000))

(defn refresh-action []
  (schedule-counter-reset)
  (re-frame/dispatch [:wallet.ui/pull-to-refresh-history]))

(defn refresh-control [refreshing?]
  (reagent/as-element
   [rn/refresh-control
    {:refreshing (boolean refreshing?)
     :onRefresh  refresh-action}]))

(defn render-asset [{:keys [icon decimals amount color value] :as token} _ _ currency]
  [quo/list-item
   {:title               [quo/text {:weight :medium}
                          [quo/text {:weight :inherit}
                           (str (if amount
                                  (wallet.utils/format-amount amount decimals)
                                  "...")
                                " ")]
                          [quo/text {:color  :secondary
                                     :weight :inherit}
                           (wallet.utils/display-symbol token)]]
    :subtitle            (str (if value value "...") " " currency)
    :accessibility-label (str (:symbol token) "-asset-value")
    :icon                (if icon
                           [wallet.components/token-icon icon]
                           [chat-icon/custom-icon-view-list (:name token) color])}])


(defn render-asset-new [{:keys [icon decimals amount color value] :as token} _ _ currency]
  [quo/list-item
   {:title               [quo/text {:weight :medium}
                          [quo/text {:weight :inherit}
                           (str (if amount
                                  (wallet.utils/format-amount amount decimals)
                                  "...")
                                " ")]
                          [quo/text {:color  :secondary
                                     :weight :inherit}
                           (wallet.utils/display-symbol token)]]
    :subtitle            (str (if value value "...") " " currency)
    :accessibility-label (str (:symbol token) "-asset-value")
    :icon                (if icon
                           [wallet.components/token-icon icon]
                           [chat-icon/custom-icon-view-list (:name token) color])}])