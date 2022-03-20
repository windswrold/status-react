(ns status-im.navigation2.core
  (:require [re-frame.core :as re-frame]
            [status-im.navigation2.roots :as roots]
            ["react-native-navigation" :refer (Navigation)]))

(def tab-key-idx {:home        0
                  :communities 1
                  :wallet      2
                  :browser     3})

;; TODO (parvesh) - improve open-modal and close-modal
(defn open-modal [comp]
  (.showModal Navigation
              (clj->js {:stack {:children
                                [{:component
                                  {:name      comp
                                   :id        comp
                                   :options   {:topBar {:visible false}}}}]}})))

(defn close-modal [_])

(defn close-all-modals []
  (.dismissAllModals Navigation))

(defn navigate [comp]
  (.push Navigation
         (name :home-stack)
         (clj->js {:component {:id      comp
                               :name    comp}})))

(re-frame/reg-fx
 :init-root-fx-nav2
 (fn [new-root-id]
   (.setRoot Navigation (clj->js (get (roots/roots) new-root-id)))))

(re-frame/reg-fx
 :change-tab-fx-nav2
 (fn [tab-id]
   (.mergeOptions Navigation "quo2-tabs-stack" (clj->js {:bottomTabs {:currentTabId tab-id}}))))

(re-frame/reg-fx :open-modal-fx2 open-modal)

(re-frame/reg-fx :close-modal-fx2 close-modal)

(re-frame/reg-fx :navigate-to-fx-nav2 navigate)
