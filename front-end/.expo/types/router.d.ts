/* eslint-disable */
import * as Router from 'expo-router';

export * from 'expo-router';

declare module 'expo-router' {
  export namespace ExpoRouter {
    export interface __routes<T extends string | object = string> {
      hrefInputParams: { pathname: Router.RelativePathString, params?: Router.UnknownInputParams } | { pathname: Router.ExternalPathString, params?: Router.UnknownInputParams } | { pathname: `/`; params?: Router.UnknownInputParams; } | { pathname: `/_sitemap`; params?: Router.UnknownInputParams; } | { pathname: `/config/Colors`; params?: Router.UnknownInputParams; } | { pathname: `/screens/map`; params?: Router.UnknownInputParams; } | { pathname: `/screens/mobileMap`; params?: Router.UnknownInputParams; } | { pathname: `/screens/search`; params?: Router.UnknownInputParams; } | { pathname: `/screens/webMap`; params?: Router.UnknownInputParams; };
      hrefOutputParams: { pathname: Router.RelativePathString, params?: Router.UnknownOutputParams } | { pathname: Router.ExternalPathString, params?: Router.UnknownOutputParams } | { pathname: `/`; params?: Router.UnknownOutputParams; } | { pathname: `/_sitemap`; params?: Router.UnknownOutputParams; } | { pathname: `/config/Colors`; params?: Router.UnknownOutputParams; } | { pathname: `/screens/map`; params?: Router.UnknownOutputParams; } | { pathname: `/screens/mobileMap`; params?: Router.UnknownOutputParams; } | { pathname: `/screens/search`; params?: Router.UnknownOutputParams; } | { pathname: `/screens/webMap`; params?: Router.UnknownOutputParams; };
      href: Router.RelativePathString | Router.ExternalPathString | `/${`?${string}` | `#${string}` | ''}` | `/_sitemap${`?${string}` | `#${string}` | ''}` | `/config/Colors${`?${string}` | `#${string}` | ''}` | `/screens/map${`?${string}` | `#${string}` | ''}` | `/screens/mobileMap${`?${string}` | `#${string}` | ''}` | `/screens/search${`?${string}` | `#${string}` | ''}` | `/screens/webMap${`?${string}` | `#${string}` | ''}` | { pathname: Router.RelativePathString, params?: Router.UnknownInputParams } | { pathname: Router.ExternalPathString, params?: Router.UnknownInputParams } | { pathname: `/`; params?: Router.UnknownInputParams; } | { pathname: `/_sitemap`; params?: Router.UnknownInputParams; } | { pathname: `/config/Colors`; params?: Router.UnknownInputParams; } | { pathname: `/screens/map`; params?: Router.UnknownInputParams; } | { pathname: `/screens/mobileMap`; params?: Router.UnknownInputParams; } | { pathname: `/screens/search`; params?: Router.UnknownInputParams; } | { pathname: `/screens/webMap`; params?: Router.UnknownInputParams; };
    }
  }
}
