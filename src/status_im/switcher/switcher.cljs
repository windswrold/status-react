(ns status-im.switcher.switcher
  (:require [quo.react-native :as rn]
            [reagent.core :as reagent]
            [status-im.switcher.styles :as styles]
            [status-im.switcher.animation :as animation]
            [status-im.ui.components.icons.icons :as icons]
            [status-im.react-native.resources :as resources]))

(def switcher-opened? (reagent/atom false))

(defn toggle-switcher-screen []
  (swap! switcher-opened? not)
  (animation/animate @switcher-opened?))

(defn switcher-button []
  [rn/touchable-opacity {:active-opacity 1
                         :on-press       toggle-switcher-screen
                         :style          (styles/switcher-button-touchable)}
   [rn/animated-view {:style (styles/switcher-close-button-background)}]
   [rn/animated-view {:style (styles/switcher-close-button-icon)}
    [icons/icon :main-icons/close {:color :white}]]
   [rn/animated-image-view {:source (resources/get-image :status-logo)
                            :style  (styles/switcher-button)}]])

(defn switcher-screen-container []
  [rn/view {:style (styles/switcher-screen-container)}])

(defn switcher-screen []
  [rn/view {:style          (styles/switcher-screen)
            :pointer-events (if @switcher-opened? :auto :none)}
   [switcher-screen-container]])

(defn switcher []
  [:<>
   [switcher-screen]
   [switcher-button]])
