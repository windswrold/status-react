(ns status-im.ui.screens.communities.channel-details
  (:require [quo.core :as quo]
            [quo.react-native :as rn]
            [taoensso.timbre :as log]
            [status-im.utils.handlers :refer [>evt <sub]]
            [status-im.ui.components.profile-header.view :as profile-header]
            [status-im.ui.components.colors :as colors]
            [status-im.i18n.i18n :as i18n]
            [clojure.string :as string]

            ))

(defn view [params]
  (let [{:keys [chat-id]} (get-in params [:route :params])
        current-chat (<sub [:chats/current-chat])
         {:keys [chat-id group-chat chat-name color description]} current-chat]
    (log/info "!! current-chat " current-chat)
    [:<>
     [quo/animated-header {:left-accessories  [{:icon                :main-icons/arrow-left
                                                :accessibility-label :back-button
                                                :on-press            #(>evt [:navigate-back])}]
                           :right-accessories [{:icon                :edit
                                                :accessibility-label :invite-button
                                                :on-press            #()}]
                           :extended-header   (profile-header/extended-header
                                               {:title    chat-name
                                                :color    color
                                                :subtitle (i18n/label :t/public-channel)
                                                })
                           :use-insets        true}
      [:<>
       (when-not (string/blank? description)
         [:<>
          [quo/list-footer {:color :main}
           description]
          [quo/separator {:style {:margin-vertical 8}}]])]]]
    ))