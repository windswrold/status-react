(ns status-im.switcher.constants
  (:require [status-im.utils.handlers :refer [<sub]]
            [status-im.utils.platform :as platform]))

(def switcher-button-radius 24)

(def switcher-button-size (* switcher-button-radius 2))

(defn switcher-bottom-position []
  (if platform/android? 17 35))

(defn switcher-center-position []
  (+ (switcher-bottom-position) (/ switcher-button-size 2)))

;; TODO(parvesh) - use different height for android and ios(Confirm from Design)
(defn bottom-tabs-height []
  (if platform/android? 55 80))

;; TODO - move to switcher/utils.cljs
(defn dimensions []
  (<sub [:dimensions/window]))
