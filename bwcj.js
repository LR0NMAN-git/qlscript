/*
微信小程序-霸王茶姬
只有签到得积分, 每天跑一两次就行
积分可以换券

授权注册后, 捉 webapi.qmai.cn 或 miniapp.qmai.cn 域名请求头里面的 Qm-User-Token, 填到变量 bwcjCookie 里面
多账号换行或@或&隔开
export bwcjCookie="H3is33xad2xxxxxxxxxxxxxxxxxx"

cron: 46 8,20 * * *
*/
const $ = new Env('霸王茶姬');

const bwcjCookie = ($.isNode() ? process.env.bwcjCookie : $.getdata('bwcjCookie')) || '';

let cookieArr = [], cookie = '', length = 0, n = 0;

// 当前时间戳
const timestamp = new Date().getTime().toString();

// 签到配置信息 - 2024年8月更新
const signConfig = {
    activityId: "1080523113114726401", // 更新的活动ID
    storeId: 49006,
    appid: "wxafec6f8422cb357b",
    timestamp: timestamp,
    signature: "262AED8C2BB8E92269C18617B34D7F1E", // 更新的签名
    data: "JUa+ygg2J78wPxD\/yt7UaDvlBA9p3ewvxSUEahZL\/PilsWqN7m5nMV9yMI+OTGRB0+jSIg9gX6w9PNs2t12eKnfSDdmM3QJjafi\/0Oc45UY6GFoSQbDVyIwOOVaZ\/spKENR+LRaNc8aFHQ0irU2cydBVxTiJ\/6RVcK1KZ3HBJ0PmrACF0nniyYTBCsVKFfvYHKl+6WZkozv7wWT3QUG0FpCU8HjyFc0iNWGOd4g342gvQnPbxm+qVbWtqTSBZ4VuN0VTVhXxIW\/XhbaJQ0Y4KA==",
    version: 3,
    x:"ffcae4dbca7a4582278e3506babcf350",
    v:2
}

!(async () => {
    if (!bwcjCookie) {
        $.log('未找到bwcjCookie，请检查环境变量设置');
        $.msg($.name, '【提示】请先获取霸王茶姬cookie', 'cookie不能为空');
        return;
    }

    // 支持多种分隔符
    if (bwcjCookie.indexOf('@') > -1) {
        cookieArr = bwcjCookie.split('@');
    } else if (bwcjCookie.indexOf('&') > -1) {
        cookieArr = bwcjCookie.split('&');
    } else if (bwcjCookie.indexOf('\n') > -1) {
        cookieArr = bwcjCookie.split('\n');
    } else {
        cookieArr = [bwcjCookie];
    }
    
    length = cookieArr.length;
    $.log(`------共${length}个账号------`);

    for (let i = 0; i < length; i++) {
        if (cookieArr[i]) {
            cookie = cookieArr[i].trim(); // 去除可能的空格
            n++;
            $.log(`------第${n}个账号签到------`);
            await userSignIn();
            // 防止接口限流
            if (i < length - 1) await $.wait(2000);
        }
    }
})()
    .catch((e) => {
        $.log('', `❌ ${$.name}, 失败! 原因: ${e}!`, '');
    })
    .finally(() => {
        $.done();
    })

function userSignIn() {
    return new Promise(resolve => {
        $.post(taskUrl(), (err, resp, data) => {
            try {
                if (err) {
                    $.log(`${JSON.stringify(err)}`);
                    $.log(`${$.name} API请求失败，请检查网路重试`);
                } else {
                    if (safeGet(data)) {
                        data = JSON.parse(data);
                        if (data.status) {
                            $.log(`今日签到成功: ${data.message}`);
                            if (data.data && data.data.point) {
                                $.log(`本次签到获得${data.data.point}积分`);
                                $.msg($.name, `签到成功`, `获得${data.data.point}积分，${data.message}`);
                            } else {
                                $.msg($.name, `签到成功`, `${data.message}`);
                            }
                        } else if (!data.status) {
                            $.log(`签到失败: ${data.message}`);
                            $.msg($.name, `签到失败`, `${data.message}`);
                        } else {
                            $.log(`异常：${JSON.stringify(data)}`);
                            $.msg($.name, `异常：${JSON.stringify(data)}`, ``);
                        }
                    }
                }
            } catch (e) {
                $.logErr(e, resp)
            } finally {
                resolve();
            }
        })
    })
}

function taskUrl() {
    return {
        url: `https://miniapp.qmai.cn/web/cmk-center/sign/takePartInSign?type__1475=eq0xnDyiG%3DY4glDlxGrtiE5iIP177iDWupD`,
        body: JSON.stringify({
            activityId: signConfig.activityId,
            storeId: signConfig.storeId,
            appid: signConfig.appid,
            timestamp: signConfig.timestamp,
            signature: signConfig.signature,
            data: signConfig.data,
            version: signConfig.version,
            x: signConfig.x,
            v: signConfig.v
        }),
        headers: {
            'Host': `miniapp.qmai.cn`,
            'Connection': 'keep-alive',
            'Accept': 'v=1.0',
            'content-type': 'application/json',
            'cookie': 'acw_tc=ac11000117479259946885121e00669013ddaa1c8206490ca934713b7ca882;ssxmod_itna3=C50qzxuD9jitiQDODcAWG0z=P0QDtzrD0nG0OlDCqD=E=W=pUNK+DUeOVG7D0HNGFznqi8DG4D8DzqGkD3L7RItxDRwoWxD5DgW4Gvwds/ixDFzD0v+Dz40WFZ7kbrpDIMH3Phb7d/lzDA5bDlPDqxGTZey=TniNonq4pABeregmzWONTjbNfnTF36PDn6cPe=fNb+0ItS2qzCoLEnY3zzMiy+MU4D;',
            'Qm-From': 'wechat',
            'Qm-From-Type': 'catering',
            'store-id': signConfig.storeId,
            'Qm-User-Token': cookie,
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.59(0x18003b2a) NetType/WIFI Language/zh_CN',
            'Referer': 'https://servicewechat.com/wxafec6f8422cb357b/240/page-frame.html'
        }
    }
}

function safeGet(data) {
    try {
        if (typeof JSON.parse(data) == "object") {
            return true;
        }
    } catch (e) {
        $.log(e);
        $.log(`访问数据为空，请检查自身设备网络情况`);
        return false;
    }
}

// prettier-ignore
function Env(t, e) {
    "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0);

    class s {
        constructor(t) {
            this.env = t
        }

        send(t, e = "GET") {
            t = "string" == typeof t ? {url: t} : t;
            let s = this.get;
            return "POST" === e && (s = this.post), new Promise((e, i) => {
                s.call(this, t, (t, s, r) => {
                    t ? i(t) : e(s)
                })
            })
        }

        get(t) {
            return this.send.call(this.env, t)
        }

        post(t) {
            return this.send.call(this.env, t, "POST")
        }
    }

    return new class {
        constructor(t, e) {
            this.name = t, this.http = new s(this), this.data = null, this.dataFile = "box.dat", this.logs = [], this.isMute = !1, this.isNeedRewrite = !1, this.logSeparator = "\n", this.startTime = (new Date).getTime(), Object.assign(this, e), this.log("", `🔔${this.name}, 开始!`)
        }

        isNode() {
            return "undefined" != typeof module && !!module.exports
        }

        isQuanX() {
            return "undefined" != typeof $task
        }

        isSurge() {
            return "undefined" != typeof $httpClient && "undefined" == typeof $loon
        }

        isLoon() {
            return "undefined" != typeof $loon
        }

        toObj(t, e = null) {
            try {
                return JSON.parse(t)
            } catch {
                return e
            }
        }

        toStr(t, e = null) {
            try {
                return JSON.stringify(t)
            } catch {
                return e
            }
        }

        getjson(t, e) {
            let s = e;
            const i = this.getdata(t);
            if (i) try {
                s = JSON.parse(this.getdata(t))
            } catch {
            }
            return s
        }

        setjson(t, e) {
            try {
                return this.setdata(JSON.stringify(t), e)
            } catch {
                return !1
            }
        }

        getScript(t) {
            return new Promise(e => {
                this.get({url: t}, (t, s, i) => e(i))
            })
        }

        runScript(t, e) {
            return new Promise(s => {
                let i = this.getdata("@chavy_boxjs_userCfgs.httpapi");
                i = i ? i.replace(/\n/g, "").trim() : i;
                let r = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");
                r = r ? 1 * r : 20, r = e && e.timeout ? e.timeout : r;
                const [o, h] = i.split("@"), n = {
                    url: `http://${h}/v1/scripting/evaluate`,
                    body: {script_text: t, mock_type: "cron", timeout: r},
                    headers: {"X-Key": o, Accept: "*/*"}
                };
                this.post(n, (t, e, i) => s(i))
            }).catch(t => this.logErr(t))
        }

        loaddata() {
            if (!this.isNode()) return {};
            {
                this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path");
                const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile),
                    s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e);
                if (!s && !i) return {};
                {
                    const i = s ? t : e;
                    try {
                        return JSON.parse(this.fs.readFileSync(i))
                    } catch (t) {
                        return {}
                    }
                }
            }
        }

        writedata() {
            if (this.isNode()) {
                this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path");
                const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile),
                    s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e), r = JSON.stringify(this.data);
                s ? this.fs.writeFileSync(t, r) : i ? this.fs.writeFileSync(e, r) : this.fs.writeFileSync(t, r)
            }
        }

        lodash_get(t, e, s) {
            const i = e.replace(/\[(\d+)\]/g, ".$1").split(".");
            let r = t;
            for (const t of i) if (r = Object(r)[t], void 0 === r) return s;
            return r
        }

        lodash_set(t, e, s) {
            return Object(t) !== t ? t : (Array.isArray(e) || (e = e.toString().match(/[^.[\]]+/g) || []), e.slice(0, -1).reduce((t, s, i) => Object(t[s]) === t[s] ? t[s] : t[s] = Math.abs(e[i + 1]) >> 0 == +e[i + 1] ? [] : {}, t)[e[e.length - 1]] = s, t)
        }

        getdata(t) {
            let e = this.getval(t);
            if (/^@/.test(t)) {
                const [, s, i] = /^@(.*?)\.(.*?)$/.exec(t), r = s ? this.getval(s) : "";
                if (r) try {
                    const t = JSON.parse(r);
                    e = t ? this.lodash_get(t, i, "") : e
                } catch (t) {
                    e = ""
                }
            }
            return e
        }

        setdata(t, e) {
            let s = !1;
            if (/^@/.test(e)) {
                const [, i, r] = /^@(.*?)\.(.*?)$/.exec(e), o = this.getval(i),
                    h = i ? "null" === o ? null : o || "{}" : "{}";
                try {
                    const e = JSON.parse(h);
                    this.lodash_set(e, r, t), s = this.setval(JSON.stringify(e), i)
                } catch (e) {
                    const o = {};
                    this.lodash_set(o, r, t), s = this.setval(JSON.stringify(o), i)
                }
            } else s = this.setval(t, e);
            return s
        }

        getval(t) {
            return this.isSurge() || this.isLoon() ? $persistentStore.read(t) : this.isQuanX() ? $prefs.valueForKey(t) : this.isNode() ? (this.data = this.loaddata(), this.data[t]) : this.data && this.data[t] || null
        }

        setval(t, e) {
            return this.isSurge() || this.isLoon() ? $persistentStore.write(t, e) : this.isQuanX() ? $prefs.setValueForKey(t, e) : this.isNode() ? (this.data = this.loaddata(), this.data[e] = t, this.writedata(), !0) : this.data && this.data[e] || null
        }

        initGotEnv(t) {
            this.got = this.got ? this.got : require("got"), this.cktough = this.cktough ? this.cktough : require("tough-cookie"), this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar, t && (t.headers = t.headers ? t.headers : {}, void 0 === t.headers.Cookie && void 0 === t.cookieJar && (t.cookieJar = this.ckjar))
        }

        get(t, e = (() => {
        })) {
            t.headers && (delete t.headers["Content-Type"], delete t.headers["Content-Length"]), this.isSurge() || this.isLoon() ? (this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, {"X-Surge-Skip-Scripting": !1})), $httpClient.get(t, (t, s, i) => {
                !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i)
            })) : this.isQuanX() ? (this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, {hints: !1})), $task.fetch(t).then(t => {
                const {statusCode: s, statusCode: i, headers: r, body: o} = t;
                e(null, {status: s, statusCode: i, headers: r, body: o}, o)
            }, t => e(t))) : this.isNode() && (this.initGotEnv(t), this.got(t).on("redirect", (t, e) => {
                try {
                    if (t.headers["set-cookie"]) {
                        const s = t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();
                        s && this.ckjar.setCookieSync(s, null), e.cookieJar = this.ckjar
                    }
                } catch (t) {
                    this.logErr(t)
                }
            }).then(t => {
                const {statusCode: s, statusCode: i, headers: r, body: o} = t;
                e(null, {status: s, statusCode: i, headers: r, body: o}, o)
            }, t => {
                const {message: s, response: i} = t;
                e(s, i, i && i.body)
            }))
        }

        post(t, e = (() => {
        })) {
            if (t.body && t.headers && !t.headers["Content-Type"] && (t.headers["Content-Type"] = "application/x-www-form-urlencoded"), t.headers && delete t.headers["Content-Length"], this.isSurge() || this.isLoon()) this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, {"X-Surge-Skip-Scripting": !1})), $httpClient.post(t, (t, s, i) => {
                !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i)
            }); else if (this.isQuanX()) t.method = "POST", this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, {hints: !1})), $task.fetch(t).then(t => {
                const {statusCode: s, statusCode: i, headers: r, body: o} = t;
                e(null, {status: s, statusCode: i, headers: r, body: o}, o)
            }, t => e(t)); else if (this.isNode()) {
                this.initGotEnv(t);
                const {url: s, ...i} = t;
                this.got.post(s, i).then(t => {
                    const {statusCode: s, statusCode: i, headers: r, body: o} = t;
                    e(null, {status: s, statusCode: i, headers: r, body: o}, o)
                }, t => {
                    const {message: s, response: i} = t;
                    e(s, i, i && i.body)
                })
            }
        }

        time(t, e = null) {
            const s = e ? new Date(e) : new Date;
            let i = {
                "M+": s.getMonth() + 1,
                "d+": s.getDate(),
                "H+": s.getHours(),
                "m+": s.getMinutes(),
                "s+": s.getSeconds(),
                "q+": Math.floor((s.getMonth() + 3) / 3),
                S: s.getMilliseconds()
            };
            /(y+)/.test(t) && (t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length)));
            for (let e in i) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? i[e] : ("00" + i[e]).substr(("" + i[e]).length)));
            return t
        }

        msg(e = t, s = "", i = "", r) {
            const o = t => {
                if (!t) return t;
                if ("string" == typeof t) return this.isLoon() ? t : this.isQuanX() ? {"open-url": t} : this.isSurge() ? {url: t} : void 0;
                if ("object" == typeof t) {
                    if (this.isLoon()) {
                        let e = t.openUrl || t.url || t["open-url"], s = t.mediaUrl || t["media-url"];
                        return {openUrl: e, mediaUrl: s}
                    }
                    if (this.isQuanX()) {
                        let e = t["open-url"] || t.url || t.openUrl, s = t["media-url"] || t.mediaUrl;
                        return {"open-url": e, "media-url": s}
                    }
                    if (this.isSurge()) {
                        let e = t.url || t.openUrl || t["open-url"];
                        return {url: e}
                    }
                }
            };
            if (this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(e, s, i, o(r)) : this.isQuanX() && $notify(e, s, i, o(r))), !this.isMuteLog) {
                let t = ["", "==============📣系统通知📣=============="];
                t.push(e), s && t.push(s), i && t.push(i), console.log(t.join("\n")), this.logs = this.logs.concat(t)
            }
        }

        log(...t) {
            t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator))
        }

        logErr(t, e) {
            const s = !this.isSurge() && !this.isQuanX() && !this.isLoon();
            s ? this.log("", `❗️${this.name}, 错误!`, t.stack) : this.log("", `❗️${this.name}, 错误!`, t)
        }

        wait(t) {
            return new Promise(e => setTimeout(e, t))
        }

        done(t = {}) {
            const e = (new Date).getTime(), s = (e - this.startTime) / 1e3;
            this.log("", `🔔${this.name}, 结束! 🕛 ${s} 秒`), this.log(), (this.isSurge() || this.isQuanX() || this.isLoon()) && $done(t)
        }
    }(t, e)
}
