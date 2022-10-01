function listingPage(consoleSlug="",gameSlug="",spriteSlug="") {
  pageType = "";
  if(spriteSlug != "" && gameSlug != "" && consoleSlug != "") {
    pageType = "sprite";
  } else if(gameSlug != "" && consoleSlug != "") {
    pageType = "game";
  } else if(consoleSlug != "") {
    pageType = "console";
  } else {
    pageType = "index";
  }

  isIndex = pageType == "index";
  isConsole = pageType == "console" || pageType == "game" || pageType == "sprite";
  isGame = pageType == "game" || pageType == "sprite";
  isSprite = pageType == "sprite";

  data = {
    "parent":   { "name": "ALttPR", "url": "https://alttpr.com" },
    "project":  { "name": "ALttPR Collection", "url": "https://snesrev.github.io/sprites-gfx" },
    "console":  { "slug": consoleSlug },
    "game":     { "slug": gameSlug },
    "sprite":   { "slug": spriteSlug }
  };

  forkMe();

  $("body").append($("<div>").attr({
    "id": "export-parts",
    "style": "float:right;text-align:right"
  }));

  sections = []
  if(isIndex) {
    sections.push("parent");
    $("title").text(data["project"]["name"]);
  }
  if(isConsole) {
    sections.push("project");
    sections.push("console");
    data["console"]["url"] = path_join([data["project"]["url"],data["console"]["slug"]]);
    // Console Title
    data["console"]["name"] = data["console"]["slug"].toUpperCase();
    $("title").text($("title").text() + ": " + data["console"]["name"]);
  }
  if(isGame) {
    sections.push("game");
    data["game"]["url"] = path_join([data["console"]["url"],data["game"]["slug"]]);
    // Game Title
    fetch_and_insert(path_join([data["game"]["url"],"lang","en.json"]),"#game-title a");
  }
  if(isSprite) {
    sections.push("sprite");
    data["sprite"]["url"] = path_join([data["game"]["url"],data["sprite"]["slug"]]);
    // Sprite Title
    // Game Manifest
    fetch_and_insert(path_join([data["game"]["url"],"manifests","manifest.json"]),"#sprite-title a");
  }

  for(let section of sections) {
    if(data[section]) {
      let text = data[section]["name"];
      let href = data[section]["url"];

      add_template(
        section + "Header",
        {
          "text": text,
          "href": href
        }
      );
    }
  }

  if(isIndex && !isConsole) {
    // Consoles List
    // console.log("Print list of Consoles for this Index");
    $("body").append($("<ul>")
      .append($("<li>")
        .append($("<a>").attr({
          "href": data["project"]["url"]
        }).text("Sprite Repository")
        )
      )
      .append($("<ul>").attr({
        "id": "index-consolelist"
      }))
    );
    fetch_and_insert(path_join([data["project"]["url"],"meta","manifests","consoles.txt"]),"#index-consolelist");
  }
  if(isConsole && !isGame) {
    // Games List for Console
    // console.log("Print list of Games for this Console");
    $("body").append($("<ul>").attr({
      "id": "console-gamelist"
    }));
    fetch_and_insert(path_join([data["console"]["url"],"games.txt"]),"#console-gamelist");
  } else if(isGame && !isSprite) {
    // Sprites List for Game
    // console.log("Print list of Sprites for this Game");
    $("body").append($("<ul>").attr({
      "id": "game-spritelist"
    }));
    // Game Manifest
    fetch_and_insert(path_join([data["game"]["url"],"manifests","manifest.json"]),"#game-spritelist");
  } else if(isSprite) {
    // Sprite Previews for Sprite
    // console.log("Print Sprite Previews for this Sprite");

    $("head").append($("<link>").attr({
      "rel": "stylesheet",
      "href": path_join([data["sprite"]["url"],"css.css"]),
      "type": "text/css"
    }));

    // Sprites Manifest
    $("#export-parts").append([
      $("<a>").attr({
        "href": path_join([data["sprite"]["url"],"sprites.json"])
      })
      .text("JSON"),

      $("<br />"),

      $("<a>").attr({
        "href": path_join([data["sprite"]["url"],"sprites.csv"])
      })
      .text("CSV"),

      $("<br />"),

      $("<a>").attr({
        "href": path_join([data["sprite"]["url"],"sprites.css"])
      })
      .text("CSS")
    ]);

    $("body").append($("<div>").attr({
      "id": "sprite-previewlist"
    }));
    // Sprites Manifest
    fetch_and_insert(path_join([data["sprite"]["url"],"sprites.json"]), "#sprite-previewlist");

    $("body").append($("<div>").attr({
      "style": "clear:both"
    }));

    $("body").append($("<ul>").attr({
      "id": "sprite-resources"
    }));
    // Layer Files Manifest
    fetch_and_insert(path_join([data["sprite"]["url"],"layer-files.json"]), "#sprite-resources");
  }
}
