(ns status-im.navigation2
  (:require [status-im.utils.fx :as fx]))

(fx/defn init-root-nav2
  {:events [:init-root-nav2]}
  [_ root-id]
  {:init-root-fx-nav2 root-id})

(fx/defn change-tab-nav2
  {:events [:navigate-change-tab-nav2]}
  [_ tab-id]
  {:change-tab-fx-nav2 tab-id})

(fx/defn open-modal-nav2
  {:events [:open-modal-nav2]}
  [_ modal]
  {:open-modal-fx-nav2 modal})

(fx/defn close-modal-nav2
  {:events [:close-modal-nav2]}
  [_ modal]
  {:close-modal-fx-nav2 modal})

(fx/defn navigate-to-nav2
  {:events [:navigate-to-nav2]}
  [cofx go-to-view-id _]
  {:navigate-to-fx-nav2 go-to-view-id})
