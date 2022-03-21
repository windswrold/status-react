(ns status-im.ui.screens.chat.styles.message.datemark
  (:require [quo.design-system.colors :as colors]))

(def datemark-mobile
  {:flex        1
   :justify-content :center
   :margin-vertical 16
   :padding-left 50})

(defn datemark-text []
  {:color colors/gray
   :font-size 14
   :line-height 16
   :font-weight "400"})
