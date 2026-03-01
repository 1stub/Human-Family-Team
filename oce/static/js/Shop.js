(function () {
  var scriptURL = 'https://sdks.shopifycdn.com/buy-button/latest/buy-button-storefront.min.js';
  if (window.ShopifyBuy) {
    if (window.ShopifyBuy.UI) {
      ShopifyBuyInit();
    } else {
      loadScript();
    }
  } else {
    loadScript();
  }
  function loadScript() {
    var script = document.createElement('script');
    script.async = true;
    script.src = scriptURL;
    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(script);
    script.onload = ShopifyBuyInit;
  }
  function ShopifyBuyInit() {
    var client = ShopifyBuy.buildClient({
      domain: 'yb2e7p-gr.myshopify.com',
      storefrontAccessToken: '0c4ccb438fe6d527864c278cfbabb781',
    });
    ShopifyBuy.UI.onReady(client).then(function (ui) {
      ui.createComponent('collection', {
        id: '325526847628',
        node: document.getElementById('collection-component-1772126707335'),
        moneyFormat: '%24%7B%7Bamount%7D%7D',
        options: {
        "product": {
            "styles": {
            "product": {
                "@media (min-width: 601px)": {
                "max-width": "calc(25% - 20px)",
                "margin-left": "20px",
                "margin-bottom": "50px",
                "width": "calc(25% - 20px)"
                },
                "img": {
                "height": "calc(100% - 15px)",
                "position": "absolute",
                "left": "0",
                "right": "0",
                "top": "0"
                },
                "imgWrapper": {
                "padding-top": "calc(75% + 15px)",
                "position": "relative",
                "height": "0"
                }
            },
            "button": {
                "font-family": "Avant Garde, sans-serif",
                "font-size": "14px",
                "padding-top": "15px",
                "padding-bottom": "15px",
                "border-radius": "18px",
                "padding-left": "58px",
                "padding-right": "58px"
            },
            "quantityInput": {
                "font-size": "14px",
                "padding-top": "15px",
                "padding-bottom": "15px"
            }
            },
            "text": {
            "button": "Add to cart"
            }
        },
        "productSet": {
            "styles": {
            "products": {
                "@media (min-width: 601px)": {
                "margin-left": "-20px"
                }
            }
            }
        },
        "modalProduct": {
            "contents": {
            "img": false,
            "imgWithCarousel": true,
            "button": false,
            "buttonWithQuantity": true
            },
            "styles": {
            "product": {
                "@media (min-width: 601px)": {
                "max-width": "100%",
                "margin-left": "0px",
                "margin-bottom": "0px"
                }
            },
            "button": {
                "font-family": "Avant Garde, sans-serif",
                "font-size": "14px",
                "padding-top": "15px",
                "padding-bottom": "15px",
                "border-radius": "18px",
                "padding-left": "58px",
                "padding-right": "58px"
            },
            "quantityInput": {
                "font-size": "14px",
                "padding-top": "15px",
                "padding-bottom": "15px"
            }
            },
            "text": {
            "button": "Add to cart"
            }
        },
        "option": {},
        "cart": {
            "styles": {
            "button": {
                "font-family": "Avant Garde, sans-serif",
                "font-size": "14px",
                "padding-top": "15px",
                "padding-bottom": "15px",
                "border-radius": "18px"
            }
            },
            "text": {
            "total": "Subtotal",
            "button": "Checkout"
            }
        },
        "toggle": {
            "styles": {
            "toggle": {
                "font-family": "Avant Garde, sans-serif"
            },
            "count": {
                "font-size": "14px"
            }
            }
        }
        },
      });
    });
  }
})();