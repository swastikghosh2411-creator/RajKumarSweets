* Hide native browser "clear" (X) button so only our custom
   .products__search-clear button shows */
.products__search-input::-webkit-search-cancel-button,
.products__search-input::-webkit-search-decoration {
  -webkit-appearance: none;
  appearance: none;
}

.products__search-input::-ms-clear,
.products__search-input::-ms-reveal {
  display: none;
  width: 0;
  height: 0;
}