(ns status-im.core
  (:require ["react-native" :as rn :refer (DevSettings)]
            [re-frame.core :as re-frame]
            [re-frame.interop :as interop]
            [reagent.core :as reagent]
            [reagent.impl.batching :as batching]))

(aset js/console "disableYellowBox" true)

(def app-registry (.-AppRegistry rn))

(defn root [_]
  (reagent/create-class
   {:display-name "root"
    :reagent-render (fn [])}))

(defn init []
  (re-frame/dispatch-sync [:init/app-started])
  (.registerComponent ^js app-registry "StatusIm" #(reagent/reactify-component root)))
