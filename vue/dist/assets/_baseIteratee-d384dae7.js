import{ck as _,cl as d,bH as c,aw as g,aV as E,cm as O,aX as P,cn as p,aT as y,be as C}from"./index-c7f6a24e.js";function I(n){return function(r){return r==null?void 0:r[n]}}var L=1,w=2;function D(n,r,e,i){var t=e.length,a=t,A=!i;if(n==null)return!a;for(n=Object(n);t--;){var f=e[t];if(A&&f[2]?f[1]!==n[f[0]]:!(f[0]in n))return!1}for(;++t<a;){f=e[t];var u=f[0],s=n[u],o=f[1];if(A&&f[2]){if(s===void 0&&!(u in n))return!1}else{var l=new _;if(i)var R=i(s,o,u,n,r,l);if(!(R===void 0?d(o,s,L|w,i,l):R))return!1}}return!0}function h(n){return n===n&&!c(n)}function G(n){for(var r=g(n),e=r.length;e--;){var i=r[e],t=n[i];r[e]=[i,t,h(t)]}return r}function M(n,r){return function(e){return e==null?!1:e[n]===r&&(r!==void 0||n in Object(e))}}function F(n){var r=G(n);return r.length==1&&r[0][2]?M(r[0][0],r[0][1]):function(e){return e===n||D(e,n,r)}}function m(n,r,e){var i=n==null?void 0:E(n,r);return i===void 0?e:i}var S=1,T=2;function b(n,r){return O(n)&&h(r)?M(P(n),r):function(e){var i=m(e,n);return i===void 0&&i===r?p(e,n):d(r,i,S|T)}}function x(n){return function(r){return E(r,n)}}function K(n){return O(n)?I(P(n)):x(n)}function U(n){return typeof n=="function"?n:n==null?y:typeof n=="object"?C(n)?b(n[0],n[1]):F(n):K(n)}export{U as b};
