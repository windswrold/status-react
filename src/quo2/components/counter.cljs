(ns quo2.components.counter
  (:require [quo.theme :as theme]
            [quo.react-native :as rn]
            [quo2.components.text :as text]
            [quo2.foundations.colors :as colors]))

(def themes
  {:light {:default    colors/primary-50
           :secondary  colors/black-opa-5
           :grey       colors/neutral-30}
   :dark  {:default    colors/primary-60
           :secondary  colors/white-opa-10
           :grey       colors/neutral-70}})

(defn get-color [key]
  (get-in themes [(theme/get-theme) key]))

(defn counter [{:keys [type outline]} label]
  (let [type       (or type :default)
        text-color (if (or
                        (= (theme/get-theme) :dark)
                        (and
                         (= type :default)
                         (not outline)))
                     colors/white
                     colors/black)]
    [rn/view {:style (merge
                      (if outline
                        {:border-width 1
                         :border-color (get-color (or type :default))}
                        {:background-color (get-color (or type :default))})
                      {:border-radius      6
                       :align-self         :center
                       :padding-vertical   2
                       :padding-horizontal 6})}
     [text/text {:weight :medium
                 :size   :label
                 :style  {:color text-color}} label]]))
