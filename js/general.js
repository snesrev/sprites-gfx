// GitHub Fork Ribbon for user contributions
function forkMe() {
  let title = "Contribute yours!";
  let stylesheet = $("<link>")
    .attr({
      "rel": "stylesheet",
      "href": "https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css",
      "type": "text/css"
    });
  let a = $("<a>")
    .attr({
      "class": "github-fork-ribbon right-top",
      "href": "https://github.com/snesrev/sprites-gfx/blob/gh-pages/CONTRIBUTING.md",
      "data-ribbon": title,
      "title": title
    })
    .text(title);
  $("head").append(stylesheet);
  $("body").append(a);
}

// Sort Fetch response HTTP status code
function status(response) {
  if(response.status >= 200 && response.status < 300) {
    return Promise.resolve(response);
  } else {
    return Promise.reject(new Error(response.statusText || "No status text"));
  }
}
// Return JSON if JSON, otherwise text
function parse(response) {
  const contentType = response.headers.get("content-type");
  if(contentType && contentType.indexOf("application/json") > -1) {
    return response.json();
  } else {
    return response.text();
  }
}
// os.path.join()
function path_join(parts=[""]) {
  return parts.join(path_sep(parts[0]))
}
// os.path.sep
function path_sep(url=window.location.href) {
  thisSep = "win";
  if(url.indexOf("http") > -1) {
    thisSep = "nix";
  }
  if(thisSep == "win") {
    return '\\';
  } else if(thisSep == "nix") {
    return '/';
  }

  // default to *nix system.
  return '/';
}
