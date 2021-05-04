(ns status-im.ui.screens.home.views
  (:require-macros [status-im.utils.views :refer [defview letsubs]])
  (:require [re-frame.core :as re-frame]
            [reagent.core :as reagent]
            [status-im.i18n.i18n :as i18n]
            [status-im.react-native.resources :as resources]
            [status-im.communities.core :as communities]
            [status-im.ui.components.connectivity.view :as connectivity]
            [status-im.ui.components.icons.icons :as icons]
            [status-im.ui.components.list.views :as list]
            [status-im.ui.components.react :as react]
            [status-im.ui.screens.home.styles :as styles]
            [status-im.ui.screens.communities.views :as communities.views]
            [status-im.ui.screens.home.views.inner-item :as inner-item]
            [status-im.ui.screens.referrals.home-item :as referral-item]
            [status-im.ui.components.colors :as colors]
            [status-im.ui.screens.add-new.new-public-chat.view :as new-public-chat]
            [quo.core :as quo]
            [status-im.add-new.core :as new-chat]
            [status-im.ui.components.search-input.view :as search-input]
            [status-im.add-new.db :as db]
            [status-im.utils.debounce :as debounce]
            [status-im.utils.utils :as utils]
            [status-im.utils.config :as config]
            [cljs-bean.core :as bean]
            [status-im.multiaccounts.login.core :as multiaccounts.login]
            [status-im.ui.components.invite.views :as invite]
            [status-im.ui.components.topbar :as topbar]
            [status-im.ui.components.plus-button :as components.plus-button]
            [status-im.ui.components.tabbar.styles :as tabs.styles]
            [status-im.ui.screens.chat.sheets :as sheets]
            [status-im.ui.components.animation :as animation]
            ["react-native-animated-math" :default animated-math]
            [quo.animated :as quo.animated])
  (:require-macros [status-im.utils.views :as views]))

(defn welcome-image-wrapper []
  (let [dimensions (reagent/atom {})]
    (fn []
      [react/view {:on-layout (fn [^js e]
                                (reset! dimensions (bean/->clj (-> e .-nativeEvent .-layout))))
                   :style     {:align-items     :center
                               :justify-content :center
                               :flex            1}}
       (let [padding    0
             image-size (- (min (:width @dimensions) (:height @dimensions)) padding)]
         [react/image {:source      (resources/get-theme-image :welcome)
                       :resize-mode :contain
                       :style       {:width image-size :height image-size}}])])))

(defn sin [animated-value]
  (.sin animated-math animated-value))

(defn cos [animated-value]
  (.cos animated-math animated-value))

(defn jump-anim [translate-anim-value scale-anim-value]
  (animation/start
   (animation/parallel
    [(animation/spring scale-anim-value {:toValue         3
                                         :damping                   200
                                         :mass                      60
                                         :stiffness                 300
                                         :overshootClamping         true
                                         :bouncyFactor              0
                                         :restSpeedThreshold        0.001
                                         :restDisplacementThreshold 0.001
                                         :easing ((animation/easing-out) (.-quad ^js animation/easing))
                                         :useNativeDriver true})
     (animation/spring translate-anim-value {:toValue         (* -1.3 Math/PI)
                                             :damping                   200
                                             :mass                      60
                                             :stiffness                 300
                                             :overshootClamping         true
                                             :bouncyFactor              0
                                             :restSpeedThreshold        0.001
                                             :restDisplacementThreshold 0.001
                                             :easing ((animation/easing-out) (.-quad ^js animation/easing))
                                             :useNativeDriver true})])
   #(do (animation/set-value translate-anim-value 0)
        (animation/set-value scale-anim-value 1))))

(defonce visible (reagent/atom false))

(defview animated-emoji [{:keys [direction top left radius v-radius translate-anim scale-anim emoji]}]
  (letsubs [width [:dimensions/window-width]]
           (let [direction-multiplier (cond
                                        (= direction :left) 1
                                        (= direction :right) -1
                                        :else 1)]
             [react/animated-view {:style {:position :absolute
                                           :top (or top 0)
                                           :left (+ (* -1 direction-multiplier radius) (/ width 2) (or left 0))
                                           :opacity (animation/interpolate
                                                     scale-anim
                                                     {:inputRange  [1 1.1 2 2.9 3]
                                                      :outputRange [0 1 1 1 0]})
                                           :transform [{:translateY (animation/multiply (sin translate-anim) v-radius)}
                                                       {:translateX (animation/multiply (cos translate-anim) (* direction-multiplier radius))}
                                                       {:scale (animation/interpolate
                                                                scale-anim
                                                                {:inputRange  [1 2 3]
                                                                 :outputRange [1 2 1.5]})}]}}
              [react/text emoji]])))

(defn animated-emojis []
  (let [translate-anim (animation/create-value 0)
        scale-anim (animation/create-value 1)
        radius-1 120
        radius-2 80
        radius-3 130
        radius-4 50
        radius-5 150
        direction-1 :left
        direction-2 :right
        direction-3 :left
        direction-4 :right
        direction-5 :right
        v-radius-1 (* radius-1 2.2)
        v-radius-2 270
        v-radius-3 230
        v-radius-4 190
        v-radius-5 (* radius-5 1.3)]
    {:component-did-mount (jump-anim translate-anim scale-anim)}
    [react/view {:style {:position :absolute
                         :top 0
                         :left 0
                         :background-color :green}}
     [animated-emoji {:top -20
                      :left 50
                      :radius radius-1
                      :v-radius v-radius-1
                      :direction direction-1
                      :translate-anim translate-anim
                      :scale-anim scale-anim
                      :emoji "🙌"}]
     [animated-emoji {:top 10
                      :left -30
                      :radius radius-2
                      :v-radius v-radius-2
                      :direction direction-2
                      :translate-anim translate-anim
                      :scale-anim scale-anim
                      :emoji "🙏"}]
     [animated-emoji {:top 20
                      :left -60
                      :radius radius-3
                      :v-radius v-radius-3
                      :direction direction-3
                      :translate-anim translate-anim
                      :scale-anim scale-anim
                      :emoji "🎉"}]
     [animated-emoji {:top 5
                      :left 40
                      :radius radius-4
                      :v-radius v-radius-4
                      :direction direction-4
                      :translate-anim translate-anim
                      :scale-anim scale-anim
                      :emoji "🎉"}]
     [animated-emoji {:top 0
                      :radius radius-5
                      :v-radius v-radius-5
                      :direction direction-5
                      :translate-anim translate-anim
                      :scale-anim scale-anim
                      :emoji "🎉"}]]))

(defn welcome []
  [react/view {:style styles/welcome-view}
       [welcome-image-wrapper]
       [react/i18n-text {:style styles/welcome-text :key :welcome-to-status}]
       [react/view
        [react/i18n-text {:style styles/welcome-text-description
                          :key   :welcome-to-status-description}]]
       [react/view {:align-items :center :margin-bottom 50}
        [quo/button {:on-press            #(swap! visible not)
                  ;;  :on-press            #(re-frame/dispatch [::multiaccounts.login/welcome-lets-go])
                     :accessibility-label :lets-go-button}
         (i18n/label :t/lets-go)]
        (when @visible [animated-emojis])]])

(defn home-tooltip-view []
  [react/view (styles/chat-tooltip)
   [react/view {:style {:flex-direction :row}}
    [react/view {:flex 1}
     [react/view {:style styles/empty-chats-header-container}
      [react/view {:style {:width       66 :position :absolute :top -6 :background-color colors/white
                           :align-items :center}}
       [react/image {:source (resources/get-image :empty-chats-header)
                     :style  {:width 50 :height 50}}]]]
     [react/touchable-highlight
      {:style               {:position :absolute :right  0  :top         0
                             :width    44        :height 44 :align-items :center :justify-content :center}
       :on-press            #(re-frame/dispatch [:multiaccounts.ui/hide-home-tooltip])
       :accessibility-label :hide-home-button}
      [icons/icon :main-icons/close-circle {:color colors/gray}]]]]
   [react/view
    [react/i18n-text {:style styles/no-chats-text :key :chat-and-transact}]]
   [invite/button]
   [react/view {:align-items :center}
    [react/view {:style (styles/hr-wrapper)}]
    [react/i18n-text {:style (styles/or-text) :key :or}]]
   [react/view {:margin-top 16}
    [react/i18n-text {:style {:margin-horizontal 16
                              :text-align        :center}
                      :key   :follow-your-interests}]
    [react/view {:style styles/tags-wrapper}
     [react/view {:flex-direction :row :flex-wrap :wrap :justify-content :center}
      (for [chat (new-public-chat/featured-public-chats)]
        (new-public-chat/render-topic chat))]]
    (when config/communities-enabled?
      [react/view
       [react/i18n-text {:style {:margin-horizontal 16
                                 :text-align        :center}
                         :key   :join-a-community}]
       [react/view {:style styles/tags-wrapper}
        [react/view {:flex-direction :row :flex-wrap :wrap :justify-content :center}
         (for [community communities/featured]
           (communities.views/render-featured-community community))]]])]])

(defn welcome-blank-page []
  [react/view {:style {:flex 1 :flex-direction :row :align-items :center :justify-content :center}}
   [react/i18n-text {:style styles/welcome-blank-text :key :welcome-blank-message}]])

(defonce search-active? (reagent/atom false))

(defn search-input-wrapper [search-filter chats-empty]
  [react/view {:padding-horizontal 16
               :padding-vertical   10}
   [search-input/search-input
    {:search-active? search-active?
     :search-filter  search-filter
     :on-cancel      #(re-frame/dispatch [:search/home-filter-changed nil])
     :on-blur        (fn []
                       (when chats-empty
                         (re-frame/dispatch [:search/home-filter-changed nil]))
                       (re-frame/dispatch [::new-chat/clear-new-identity]))
     :on-focus       (fn [search-filter]
                       (when-not search-filter
                         (re-frame/dispatch [:search/home-filter-changed ""])
                         (re-frame/dispatch [::new-chat/clear-new-identity])))
     :on-change      (fn [text]
                       (re-frame/dispatch [:search/home-filter-changed text])
                       (re-frame/dispatch [:set-in [:contacts/new-identity :state] :searching])
                       (debounce/debounce-and-dispatch [:new-chat/set-new-identity text] 300))}]])

(defn start-suggestion [search-value]
  (let [{:keys [state ens-name public-key]}
        @(re-frame/subscribe [:contacts/new-identity])
        valid-private? (= state :valid)
        valid-public?  (db/valid-topic? search-value)]
    (when (or valid-public? valid-private?)
      [react/view
       [quo/list-header (i18n/label :t/search-no-chat-found)]
       (when valid-private?
         [quo/list-item {:theme    :accent
                         :icon     :main-icons/private-chat
                         :title    (or ens-name (utils/get-shortened-address public-key))
                         :subtitle (i18n/label :t/join-new-private-chat)
                         :on-press (fn []
                                     (debounce/dispatch-and-chill [:contact.ui/contact-code-submitted false] 3000)
                                     (re-frame/dispatch [:search/home-filter-changed nil]))}])
       (when valid-public?
         [quo/list-item {:theme    :accent
                         :icon     :main-icons/public-chat
                         :title    (str "#" search-value)
                         :subtitle (i18n/label :t/join-new-public-chat)
                         :on-press (fn []
                                     (re-frame/dispatch [:chat.ui/start-public-chat search-value])
                                     (re-frame/dispatch [:set :public-group-topic nil])
                                     (re-frame/dispatch [:search/home-filter-changed nil]))}])])))

(defn render-fn [{:keys [chat-id] :as home-item}]
  ;; We use `chat-id` to distinguish communities from chats
  (if chat-id
    [inner-item/home-list-item
     home-item
     {:on-press      (fn []
                       (re-frame/dispatch [:dismiss-keyboard])
                       (re-frame/dispatch [:chat.ui/navigate-to-chat chat-id])
                       (re-frame/dispatch [:search/home-filter-changed nil]))
      :on-long-press #(re-frame/dispatch [:bottom-sheet/show-sheet
                                          {:content (fn []
                                                      [sheets/actions home-item])}])}]
    [communities.views/community-home-list-item home-item]))

(defn chat-list-key-fn [item]
  (or (:chat-id item) (:id item)))

(defn get-item-layout [_ index]
  #js {:length 64 :offset (* 64 index) :index index})

(views/defview communities-and-chats []
  (views/letsubs [{:keys [items search-filter]} [:home-items]
                  hide-home-tooltip? [:hide-home-tooltip?]]
    (if (and (empty? items)
             (empty? search-filter)
             hide-home-tooltip?
             (not @search-active?))
      [welcome-blank-page]
      [list/flat-list
       {:key-fn                       chat-list-key-fn
        :getItemLayout                get-item-layout
        :initialNumToRender           5
        :keyboard-should-persist-taps :always
        :data                         items
        :render-fn                    render-fn
        :header                       [:<>
                                       (when (or (seq items) @search-active? (seq search-filter))
                                         [search-input-wrapper search-filter (empty? items)])
                                       [referral-item/list-item]
                                       (when (and (empty? items)
                                                  (or @search-active? (seq search-filter)))
                                         [start-suggestion search-filter])]
        :footer                       (if (and (not hide-home-tooltip?) (not @search-active?))
                                        [home-tooltip-view]
                                        [react/view {:height 68}])}])))

(views/defview chats-list []
  (views/letsubs [loading? [:chats/loading?]]
    [:<>
     [connectivity/loading-indicator]
     (if loading?
       [react/view {:flex 1 :align-items :center :justify-content :center}
        [react/activity-indicator {:animating true}]]
       [communities-and-chats])]))

(views/defview plus-button []
  (views/letsubs [logging-in? [:multiaccounts/login]]
    [components.plus-button/plus-button
     {:on-press (when-not logging-in?
                  #(re-frame/dispatch [:bottom-sheet/show-sheet :add-new {}]))
      :loading logging-in?
      :accessibility-label :new-chat-button}]))

(views/defview notifications-button []
  (views/letsubs [notif-count [:activity.center/notifications-count]]
    [react/view
     [quo/button {:type     :icon
                  :style {:margin-left 10}
                  :accessibility-label "notifications-button"
                  :on-press #(do
                               (re-frame/dispatch [:mark-all-activity-center-notifications-as-read])
                               (re-frame/dispatch [:navigate-to :notifications-center]))
                  :theme    :icon}
      :main-icons/notification]
     (when (pos? notif-count)
       [react/view {:style (merge (tabs.styles/counter-public-container) {:top 5 :right 5})
                    :pointer-events :none}
        [react/view {:style               tabs.styles/counter-public
                     :accessibility-label :notifications-unread-badge}]])]))

(defn home []
  [react/keyboard-avoiding-view {:style {:flex 1}}
   [topbar/topbar {:title           (i18n/label :t/chat)
                   :navigation      :none
                   :right-component [react/view {:flex-direction :row :margin-right 16}
                                     [connectivity/connectivity-button]
                                     [notifications-button]]}]
   [chats-list]
   [plus-button]])
