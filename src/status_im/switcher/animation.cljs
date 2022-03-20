(ns status-im.switcher.animation
  (:require [quo.react-native :as rn]
            [reagent.core :as reagent]
            [status-im.switcher.constants :as constants]
            [status-im.ui.components.animation :as anim]))

(def bottom-tabs-opacity (anim/create-value 1))
(def switcher-button-opacity (anim/create-value 1))
(def switcher-close-button-icon-opacity (anim/create-value 0))
(def switcher-close-button-background-opacity (anim/create-value 0))
(def bottom-tabs-position (anim/create-value 0))
(def switcher-screen-radius (reagent/atom 1))
(def layout-animation #js {:duration 300
                           :create   #js {:type     (:ease-in-ease-out rn/layout-animation-types)
                                          :property (:scale-xy rn/layout-animation-properties)}
                           :update   #js {:type     (:ease-in-ease-out rn/layout-animation-types)
                                          :property (:scale-xy rn/layout-animation-properties)}
                           :delete   #js {:type     (:ease-in-ease-out rn/layout-animation-types)
                                          :property (:scale-xy rn/layout-animation-properties)}})

(defn animate-layout [show?]
  (let [{:keys [width height]} (constants/dimensions)
        target-radius          (- (max width height)
                                  constants/switcher-button-radius)]
    (rn/configure-next layout-animation)
    (reset! switcher-screen-radius (if show? target-radius 1))
    (reagent/flush)))

(defn timing-animation [property toValue]
  (anim/timing property {:toValue         toValue
                         :duration        300
                         :useNativeDriver true}))

(defn animate-components [show?]
  (anim/start
   (anim/parallel
    [(timing-animation bottom-tabs-opacity (if show? 0 1))
     (timing-animation switcher-button-opacity (if show? 0 1))
     (timing-animation switcher-close-button-icon-opacity (if show? 1 0))
     (timing-animation switcher-close-button-background-opacity (if show? 0.2 0))
     (timing-animation bottom-tabs-position (if show? (constants/bottom-tabs-height) 0))])))

(defn animate [show?]
  (animate-layout show?)
  (animate-components show?))
