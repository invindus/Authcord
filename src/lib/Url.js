import {getBasicHeaderValue} from "./User";

export function makeLocalUrl(postFix) {
    let hasLeadingSlash = postFix.startsWith("/");
    let prefix = "/api/";
    return prefix + postFix.substring(hasLeadingSlash ? 1 : 0);
}

export async function fetchLocal(route, options = {}) {
    let opt = options;
    if (!("headers" in options)) {
        opt.headers = {};
    }
    opt.headers["X-Send-Localized-Identification"] = "1";
    return fetch(makeLocalUrl(route), opt);
}

export async function fetchLocalWithBasic(route, options={}) {
    let opt = options;
    if (!("headers" in options)) {
        opt.headers = {};
    }
    opt.headers.Authorization = getBasicHeaderValue();
    return fetchLocal(route, opt);
}
