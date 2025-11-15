/**
 * This file updates the board and the character dialogue on the home page.
 *
 * It ensures the clickable block areas are the right size by resizing them
 * when the img element detects a size change, so the parent container does
 * not need to be restricted to a certain size.
 *
 * It also changes the character's name and image, as well as the block name
 * and description, in the character dialogue to the right of the interactive
 * board. It grabs the character name, character image, block name, and
 * block description from the board.html attributes, which are unique
 * to each block.
 */

const BLOCK_NAME = document.getElementById("block-name");
const BLOCK_NUMBER = document.getElementById("block-number");
const BLOCK_PLACEHOLDER = document.getElementById("block-placeholder");

const CHARACTER_NAME = document.getElementById("character-name");
const CHARACTER_IMG = document.getElementById("character-img");
const CHARACTER_PLURAL_S = document.getElementById("character-plural-s");

/**
 * 500 pixels was the original image size when the block
 * areas were defined. THIS SHOULDN'T CHANGE!
 *
 * The original area coords are stored here because if only the
 * most recent area coords are rescaled repeatedly, rounding
 * error will accumulate and deform the areas.
 */
const ORIGINALWIDTH = 500;
const ORIGINALCOORDS = (() => {
  let temp = {};

  document.querySelectorAll("area").forEach((area) => {
    temp[area.getAttribute("id")] = area.getAttribute("coords");
  });

  return temp;
})();

function setupBlockAreas() {
  // as the parent element of the game board changes,
  // adjust the size of the image
  let wrapperWidth = document.querySelector("#map-wrapper").clientWidth;

  let boardImage = document.querySelector("#game-board-image");
  boardImage.setAttribute("width", parseInt(wrapperWidth));
  boardImage.setAttribute("height", parseInt(wrapperWidth));

  // adjust the size of the map areas to match the image
  resizeBlockAreas();

  // adjust the size of the canvas over the map
  // (with a stroke width that corresponds to the size)
  $(function () {
    $(".map").maphilight({
      strokeWidth: Math.round(wrapperWidth / 100),
    });
  });
}

function resizeBlockAreas() {
  let newWidth = document
    .querySelector("#game-board-image")
    .getAttribute("width");

  document.querySelectorAll("area").forEach((area) => {
    // grab the coords and convert the string to an array of nums
    let newCoords = ORIGINALCOORDS[area.getAttribute("id")]
      .split(",")
      .map((num) => {
        return parseInt(num);
      });

    // rescale the coords
    newCoords = newCoords.map((num) => {
      return Math.round(num * ((newWidth * 1.0) / ORIGINALWIDTH));
    });

    area.setAttribute("coords", newCoords.join(","));
  });
}

function setBlockLabel(e) {
  if (
    e.target.tagName.toLowerCase() === "area" &&
    e.target.parentElement.getAttribute("name") === "game-board-map"
  ) {
    let blockName = e.target.getAttribute("alt");
    let blockNumber = e.target.getAttribute("id").split("-");

    // capitalize blockNumber words
    blockNumber = blockNumber.map((word) => {
      return word[0].toUpperCase() + word.substr(1);
    });

    let blockColor =
      "#" + JSON.parse(e.target.getAttribute("data-maphilight"))["strokeColor"];

    BLOCK_NUMBER.innerText = blockNumber.join(" ");
    BLOCK_NUMBER.style.color = blockColor;
    BLOCK_PLACEHOLDER.innerText = " in ";

    BLOCK_NAME.innerText = blockName;
    BLOCK_NAME.style.color = blockColor;

    let names = e.target.getAttribute("data-character-name");

    CHARACTER_NAME.innerText = names;
    CHARACTER_PLURAL_S.innerText = names.split(" ").length > 1 ? "" : "s";
    CHARACTER_IMG.setAttribute(
      "src",
      e.target.getAttribute("data-character-img-url"),
    );
  }
}

function resetBlockLabel(e) {
  // reset fields to placeholders
  if (e.target.getAttribute("id") === "game-board-image") {
    BLOCK_NUMBER.innerText = "";
    BLOCK_PLACEHOLDER.innerText = " each block by clicking one on the board!";

    BLOCK_NAME.innerText = "";

    CHARACTER_NAME.innerText = "Ambassadors";
    CHARACTER_PLURAL_S.innerText = "s";
    CHARACTER_IMG.setAttribute("src", "/static/images/ambassadors.jpg");
  }
}

window.addEventListener("resize", setupBlockAreas);
document.addEventListener("DOMContentLoaded", setupBlockAreas);
document.addEventListener("mouseover", setBlockLabel);
document.addEventListener("mouseout", resetBlockLabel);
