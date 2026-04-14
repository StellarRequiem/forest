# Quarantined code - Forest Warden
# Description: Scouted content: uBlock privacy list

# Fetched content from https://raw.githubusercontent.com/ublockorigin/uAssets/master/filters/privacy.txt
# Description: uBlock privacy list

print('Content length:', len('''! Title: uBlock filters – Privacy
! Last modified: %timestamp%
! Expires: 7 days
! Description: |
!   Some of these filters make use of the `important` filter option,`
!   which purpose is to guarantee that a filter won't be overriden by
!   exception filters.
! License: https://github.com/uBlockOrigin/uAssets/blob/master/LICENSE
! Homepage: https://github.com/uBlockOrigin/uAssets
!
! GitHub issues: https://github.com/uBlockOrigin/uAssets/issues
! GitHub pull requests: https://github.com/uBlockOrigin/uAssets/pulls

! Redirect to neutered Google Analytics
||google-analytics.com/analytics.js$script,xhr,redirect=google-analytics_analytics.js:5

! Redirect to neutered Google Analytics Experiments
||google-analytics.com/cx/api.js$script,redirect=google-analytics.com/cx/api.js:5

! https://www.reddit.com/r/uBlockOrigin/comments/xif3tf/
||googletagmanager.com/gtag/js$script,xhr,redirect=googletagmanager_gtm.js:5
! https://github.com/uBlockOrigin/uAssets/issues/29730
||googletagmanager.com/gtag/js?id=$removeparam=gtm
||googletagmanager.com/gtag/js?id=$removeparam=cx

! https://github.com/gorhill/uBlock/issues/1411
! https://www.reddit.com/r/firefox/comments/3pwcey/firefox_extension_download_manager_s3_asks_for/
! https://www.reddit.com/r/chrome/comments/473ves/help_how_to_remove_qipru_redirect_when_searching/
||lnkr.us^$doc
||icontent.us^$doc
||qip.ru^$doc
! https://github.com/gorhill/uBlock/issues/1411#issuecomment-201031771
||ratexchange.net^
||adnotbad.com^
||serverads.net^
||tradeadsexchange.com^

! https://www.reddit.com/r/ublock/comments/47o2ih/ublock_disabling_all_javascript_links/d0fhock
! Time to bring this filter out of experimental status
||googletagservices.com/tag/js/gpt.js$script,xhr,redirect=googletagservices.com/gpt.js:5
||securepubads.g.doubleclick.net/tag/js/gpt.js$script,redirect=googletagservices_gpt.js:5
||pagead2.googlesyndication.com/tag/js/gpt.js$script,redirect=googletagservices_gpt.js:5

! https://github.com/gorhill/uBlock/issues/1265
||scorecardresearch.com/beacon.js$script,redirect=scorecardresearch.com/beacon.js:5

! https://github.com/uBlockOrigin/uAssets/issues/7
||google-analytics.com/ga.js$script,redirect=google-analytics.com/ga.js:5

! https://www.eff.org/deeplinks/2014/07/white-house-website-includes-unique-non-cookie-tracker-despite-privacy-policy
! https://github.com/uBlockOrigin/uAssets/issues/1713
! https://github.com/uBlockOrigin/uAssets/issues/6319
! https://github.com/gorhill/uBlock/issues/1384
! https://github.com/uBlockOrigin/uAssets/issues/11003
||addthis.com/*/addthis_widget.js$script
##.addthis_toolbox

! Examples of what is fixed by even an unfilled dummy API:
! https://twitter.com/kenn_butler/status/709163241021317120
! https://adblockplus.org/forum/viewtopic.php?f=10&t=48183
! https://forums.lanik.us/viewtopic.php?f=64&t=32161
! https://forums.lanik.us/viewtopic.php?f=64&t=30670
! https://github.com/uBlockOrigin/uAssets/issues/30853
||googletagmanager.com/gtm.js$script,redirect=googletagmanager_gtm.js:5,domain=~nerc.com

! https://github.com/gorhill/uBlock/issues/1082
! https://github.com/gorhill/uBlock/issues/1250#issuecomment-173533894
! https://github.com/gorhill/uBlock/issues/2155
||widgets.outbrain.com/outbrain.js$script,redirect=outbrain-widget.js:5,domain=~vice.com

! https://github.com/uBlockOrigin/uAssets/issues/713
||google-analytics.com/analytics.js$important,script,redirect=google-analytics.com/analytics.js,domain=support.amd.com
||googletagmanager.com/gtm.js$important,script,redirect=googletagmanager.com/gtm.js,domain=support.amd.com

! https://github.com/uBlockOrigin/uAssets/issues/4138
rediff.com##a[onclick^="trackURL"]:remove-attr(onclick)
rediff.com##a[onmousedown^="return enc(this,'https://track.rediff.com"]:remove-attr(onmousedown)

! https://www.reddit.com/r/uBlockOrigin/comments/b9qsix/new_reddit_tracks_a_ton_more_data_someone_said/
! https://github.com/uBlockOrigin/uAssets/commit/5563840a319a26025290e17f4e9401b201ac2b99#commitcomment-118042265
||reddit.com/api/jail^$xhr,1p
! https://www.reddit.com/r/uBlockOrigin/comments/tihpyw/oldredditcom_outbound_tracking_via_out_reddit_com/i1f290z/?context=3
old.reddit.com##a.outbound[data-outbound-url]:remove-attr(data-outbound-url)
!reddit.com##+js(set, Object.prototype.allowClickTracking, false)
! https://www.reddit.com/r/worldnews/
! https://github.com/uBlockOrigin/uAssets/issues/18938
www.reddit.com##+js(json-prune, data.*.elements.edges.[].node.outboundLink)
www.reddit.com##+js(json-prune, data.children.[].data.outbound_link)
||reddit.com^$doc,removeparam=/web_only=/
||reddit.com^$doc,removeparam=/deep_link=/
||reddit.com^$doc,removeparam=correlation_id
||reddit.com^$doc,removeparam=ref
||reddit.com^$doc,removeparam=ref_campaign
||reddit.com^$doc,removeparam=ref_source
||reddit.com^$doc,removeparam=utm_content
! https://github.com/uBlockOrigin/uBlock-issues/issues/3206#issuecomment-2406041484
||click.redditmail.com/CL0/$urlskip=/\/CL0\/(http.*?)\/\d\/[a-f0-9-]+\// -uricomponent
! remove.bg
||rd.remove.bg/CL0/http$doc,urlskip=/\/CL0\/(http.*?)\/\d\/[a-f0-9-]+\// -uricomponent

! https://github.com/uBlockOrigin/uAssets/pull/5997
docs.google.com##+js(no-xhr-if, method:POST url:/logImpressions)
! https://github.com/uBlockOrigin/uAssets/issues/7960
www.google.*##+js(set, rwt, noopFunc)
! https://github.com/uBlockOrigin/uAssets/issues/7960#issuecomment-2018914258
!#if !env_mobile
www.google.*###main a[href][data-sb^="/url?"]:remove-attr(data-sb)
!#else
www.google.*##+js(href-sanitizer, #main a[href^="/url?q=http"], ?q)
www.google.*###main a[href][ping^="/url?"]:remove-attr(ping)
!#endif
||www.google.*/url?sa=*&source=*&cd=&ved=*&url=$urlskip=?url,doc,1p
! https://www.reddit.com/r/uBlockOrigin/comments/1eppef9/is_it_possible_to_hide_googles_annoying_redirect/
www.google.*##+js(set-attr, c-wiz[data-p] [data-query] a[target="_blank"][role="link"], rlhc, 1)

! https://github.com/uBlockOrigin/uAssets/issues/6538
liberation.fr,officedepot.fr,oui.sncf##+js(acs, document.createElement, '.js')
sfr.fr##+js(aopr, _oEa)

! https://github.com/uBlockOrigin/uBlock-issues/issues/780#issuecomment-558734257
brillen.de##+js(acs, document.createElement, 'script')
||marketing.net.*^$1p

! https://github.com/uBlockOrigin/uAssets/issues/7118
||vidtech.cbsinteractive.com^*/tracking/$script,redirect=noop.js,important

! https://github.com/uBlockOrigin/uAssets/issues/7178
!#if env_chromium
||carsensor.net/usedcar/modules/clicklog_$xhr,1p,important,redirect=noop.txt
!#endif

! https://github.com/uBlockOrigin/uAssets/issues/478#issuecomment-612229916
/analytics/analytics.$~xmlhttprequest,3p
/googleanalytics.js$3p
! https://github.com/uBlockOrigin/uAssets/issues/11262
-google-analytics/$domain=~wordpress.org,badfilter
-google-analytics/$3p,domain=~wordpress.org|~brookson.co.uk

! https://github.com/uBlockOrigin/uAssets/pull/4961
||the-japan-news.com/modules/js/lib/fgp/fingerprint2.js$script,redirect=fingerprint2.js,important

! https://github.com/AdguardTeam/AdguardFilters/issues/57295
||mtsa.com.my/mtcs.php/pageview/track^$image

! https://github.com/AdguardTeam/AdguardFilters/issues/57325
||api.tumblr.com/*/share/stats$script,3p

! https://github.com/uBlockOrigin/uAssets/issues/7833
frogogo.ru##+js(aopw, ADMITAD)
||artfut.com/static/tagtag.$script,3p,redirect=noop.js

! https://github.com/uBlockOrigin/uAssets/issues/8105
! block known tracking honeypots
||copyhomework.com^
||coursecopy.com^
||quiztoolbox.com^
||quizlookup.com^
||studyeffect.com^
||testbooksolutions.com^

! https://github.com/uBlockOrigin/uBlock-issues/issues/1388
@@||googletagmanager.com/gtm.js$script,redirect-rule,domain=rocketnews24.com

! https://github.com/uBlockOrigin/uAssets/commit/ee5aec09e45376b7e6fb50ff56cb54425826df0d#commitcomment-44879744
/stats.php?*event=$image

! beastpics.club etc.
/check.php?t=*&rand=$image,1p

! https://github.com/uBlockOrigin/uAssets/issues/6694
||recommend.9gag.com/interact/event/?ip

! https://github.com/easylist/easylist/issues/6724
/jquery.js?*&rx=*&foxtail=$image,1p
||jsdelivr.net/npm/skx@*/optical.js

! hd21 group sites analytics
/counter/?domain=$image,1p
||hd21.com/ajax/track?

! drtuber.desi analytics
||drtuber.*/ajax/track?track_type=

! dekki.com analytics
||playbrain.io/analytics/

! https://github.com/AdguardTeam/AdguardFilters/issues/80625
tweakers.net##+js(aost, btoa, send)

! https://github.com/AdguardTeam/AdguardFilters/issues/81533
||yuktamedia.com^$3p

! https://github.com/AdguardTeam/AdguardFilters/issues/81778
||gamedock.io^$3p

! https://github.com/AdguardTeam/AdguardFilters/issues/75098
||stats.webgames.io^

! https://github.com/uBlockOrigin/uAssets/issues/9273
||blogfoster.com^$3p

! mettablog.com
||myanalytic.net^$3p

! simply-hentai.com beacon
||t.simply-hentai.com^

! https://search.brave.com/search?q=Chromium
search.brave.com##+js(no-fetch-if, body:browser)

! https://github.com/uBlockOrigin/uAssets/pull/9472
||d3bch4rrbnbe5n.cloudfront.net/pxl.png^

! https://github.com/uBlockOrigin/uAssets/issues/9123
/visilabs.min.js

! https://github.com/orgs/uBlockOrigin/teams/ublock-filters-volunteers/discussions/354
||civicscience.com^$3p

! https://github.com/uBlockOrigin/uAssets/issues/9932
/\/[a-z0-9]{12}\/[a-zA-Z0-9\/\+\-]{97,106}$/$match-case,script,1p,strict1p
/^https?:\/\/(?!assets|script|static)(?:[0-9a-z]{10,13}|[0-9a-z]{6})\.[0-9A-Za-z.\-_]+\/(?=[0-9a-z+\/\-]*[A-Z])[0-9A-Za-z+\/\-]{80,106}$/$script,1p,match-case,strict3p
/dataunlocker$script,1p,domain=~dataunlocker.com
||data-saver-cindi.herokuapp.com^
||franchiseplus.nl^$csp=script-src * 'unsafe-inline' 'wasm-unsafe-eval' data: blob: mediastream: filesystem:
||a.stateless.me^
dataunlocker.com,androidacy.com,bolighub.dk##+js(set, _hjSettings, undefined)
dataunlocker.com,androidacy.com,bolighub.dk##+js(set, google_tag_manager, undefined)
@@||stats.g.doubleclick.net/g/$xhr,domain=androidacy.com
||stats.g.doubleclick.net/g/$removeparam,domain=androidacy.com
!#if cap_html_filtering
||dataunlocker.com/d/$script,1p,replace=/Copyright .*//s
/\/[1-z0-9]{10,20}\/[1-z0-9]{60,300}$/$script,1p,replace=/Copyright .*//s,domain=androidacy.com|bolighub.dk
comicleaks.com,ping.gg,nookgaming.com,creatordrop.com,bitdomain.biz,fort-shop.kiev.ua,accuretawealth.com,tracktheta.com,adaptive.marketing,camberlion.com,segops.madisonspecs.com,stresshelden-coaching.de,controlconceptsusa.com,ryaktive.com,tip.etip-staging.etip.io##^script:has-text("join('')")
furucombo.app##^script:has-text('join("")')
intercity.technology,freelancer.taxmachine.be,kodalia.com,adria.gg,fjlaboratories.com,abhijith.page,helpmonks.com##^script:has-text(api.dataunlocker.com)
dataunlocker.com##^script:has-text(/^Function\(\"/)
!#else
comicleaks.com,ping.gg,nookgaming.com,creatordrop.com,bitdomain.biz,fort-shop.kiev.ua,accuretawealth.com,tracktheta.com,adaptive.marketing,camberlion.com,segops.madisonspecs.com,stresshelden-coaching.de,controlconceptsusa.com,ryaktive.com,tip.etip-staging.etip.io##+js(rmnt, script, /join\(\'\'\)/)
furucombo.app##+js(rmnt, script, /join\(\"\"\)/)
intercity.technology,freelancer.taxmachine.be,adria.gg,fjlaboratories.com,abhijith.page,helpmonks.com##+js(rmnt, script, api.dataunlocker.com)
dataunlocker.com##+js(rmnt, script, /^Function\(\"/)
!#endif

! https://www.reddit.com/r/uBlockOrigin/comments/opoba7/washington_post_showing_ad_placeholders/
||washpost.nile.works^

! https://github.com/easylist/easylist/commit/6457d9a221b19bf6d011d314d0bf14476d18f428#commitcomment-54257940
/p13n/batch/action/*$image

! Ad-Shield
! https://github.com/uBlockOrigin/uAssets/issues/9717
/^https:\/\/cdn\.jsdelivr\.net\/npm\/[-a-z_]{4,22}@latest\/dist\/script\.min\.js$/$script,3p,match-case
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, adshield-analytics-uuid, $remove$)
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, /_fa_bGFzdF9iZmFfYXQ=$/, $remove$)
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, /_fa_dXVpZA==$/, $remove$)
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, /_fa_Y2FjaGVfaXNfYmxvY2tpbmdfYWNjZXB0YWJsZV9hZHM=$/, $remove$)
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, /_fa_Y2FjaGVfaXNfYmxvY2tpbmdfYWRz$/, $remove$)
373news.com,aikatu.jp,aniroleplay.com,ap7am.com,areaconnect.com,as-web.jp,aucfree.com,autoby.jp,autoc-one.jp,autofrage.net,automobile-catalog.com,bab.la,babla.*,badmouth1.com,bamgosu.site,bg-mania.jp,bien.hu,bleepingcomputer.com,blogmura.com,buzzfeed.com,buzzfeednews.com,cesoirtv.com,chanto.jp.net,cinema.com.my,cinetrafic.fr,cocokara-next.com,collinsdictionary.com,computerfrage.net,convertcase.net,cool-style.com.tw,crosswordsolver.com,cruciverba.it,cults3d.com,daily.co.jp,dailynewshungary.com,dayspedia.com,dictionary.cambridge.org,dnevno.hr,dogdrip.net,dolldivine.com,donbalon.com,dramabeans.com,dropgame.jp,dziennik.pl,economictimes.com,economist.co.kr,edaily.co.kr,etoday.co.kr,etoland.co.kr,eurointegration.com.ua,ev-times.com,filmibeat.com,flatpanelshd.com,fntimes.com,footballtransfer.com.ua,footballtransfer.ru,forsal.pl,freemcserver.net,fxstreet-id.com,fxstreet-vn.com,fxstreet.*,gazetaprawna.pl,genialetricks.de,giornalone.it,globalrph.com,gloria.hr,golf-live.at,goodreturns.in,hb-nippon.com,heureka.cz,hometownstation.com,honkailab.com,horairesdouverture24.fr,hotcopper.com.au,idokep.hu,infinityfree.com,iplocation.net,islamicfinder.org,isplus.com,issuya.com,iusm.co.kr,j-cast.com,j-town.net,j7p.jp,jablickar.cz,jamaicaobserver.com,javatpoint.com,jawapos.com,jmty.jp,joemonster.org,judgehype.com,jutarnji.hr,kinmaweb.jp,km77.com,knowt.com,kobe-journal.com,kompasiana.com,kreuzwortraetsel.de,kurashinista.jp,kurashiru.com,kyoteibiyori.com,lacuarta.com,lakeshowlife.com,laleggepertutti.it,lamire.jp,ldoceonline.com,leckerschmecker.me,lifehacker.jp,listentotaxman.com,livenewschat.eu,loawa.com,logicieleducatif.fr,mahjongchest.com,maketecheasier.com,malaymail.com,mamastar.jp,manta.com,mathplayzone.com,mediaindonesia.com,mentalfloss.com,meteo60.fr,midhudsonnews.com,minesweeperquest.com,minkou.jp,missyusa.com,mlbpark.donga.com,moin.de,motor-talk.de,motscroises.fr,muragon.com,mykhel.com,mynet.com,nana-press.com,nationaltoday.com,nbadraft.net,netzwelt.de,newsinlevels.com,newsweekjapan.jp,niice-woker.com,niketalk.com,nouvelobs.com,oeffnungszeitenbuch.de,ondemandkorea.com,onlineradiobox.com,optionsprofitcalculator.com,oraridiapertura24.it,oxfordlearnersdictionaries.com,palabr.as,pashplus.jp,persoenlich.com,petitfute.com,picksandparlays.net,picrew.me,powerpyx.com,pptvhd36.com,pravda.com.ua,pressian.com,profitline.hu,puzzlegarage.com,quefaire.be,radio-australia.org,radio-osterreich.at,raenonx.cc,raetsel-hilfe.de,references.be,relevantmagazine.com,reportera.co.kr,roleplayer.me,rostercon.com,samsungmagazine.eu,scribens.com,scribens.fr,slashdot.org,slobodnadalmacija.hr,smsonline.cloud,soccerdigestweb.com,solitairehut.com,sourceforge.net,southhemitv.com,sportalkorea.com,sportanalytic.com,sportsrec.com,sportsseoul.com,szamoldki.hu,talkwithstranger.com,tasty.co,tbsradio.jp,text-compare.com,thatgossip.com,the-crossword-solver.com,thedigestweb.com,thefreebieguy.com,tportal.hr,traicy.com,transparentcalifornia.com,transparentnevada.com,tunebat.com,tvtv.ca,tvtv.us,tweaktown.com,twn.hu,tyda.se,tz.de,ufret.jp,upmedia.mg,verkaufsoffener-sonntag.com,w.grapps.me,watchdocumentaries.com,webdesignledger.com,welt.de,wfmz.com,winfuture.de,word-grabber.com,worldhistory.org,worldjournal.com,wort-suchen.de,woxikon.*,yakkun.com,ygosu.com,yutura.net,zagreb.info,zakzak.co.jp##+js(set-local-storage-item, /_fa_Y2FjaGVfYWRibG9ja19jaXJjdW12ZW50X3Njb3Jl$/, $remove$)
! livedoor-sites
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, adshield-analytics-uuid, $remove$)
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, /_fa_bGFzdF9iZmFfYXQ=$/, $remove$)
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, /_fa_dXVpZA==$/, $remove$)
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, /_fa_Y2FjaGVfaXNfYmxvY2tpbmdfYWNjZXB0YWJsZV9hZHM=$/, $remove$)
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, /_fa_Y2FjaGVfaXNfYmxvY2tpbmdfYWRz$/, $remove$)
2chblog.jp,2monkeys.jp,46matome.net,akb48glabo.com,akb48matomemory.com,alfalfalfa.com,all-nationz.com,anihatsu.com,aqua2ch.net,blog.esuteru.com,blog.livedoor.jp,blog.jp,blogo.jp,chaos2ch.com,choco0202.work,crx7601.com,danseisama.com,dareda.net,digital-thread.com,doorblog.jp,exawarosu.net,fgochaldeas.com,football-2ch.com,gekiyaku.com,golog.jp,hacchaka.net,heartlife-matome.com,liblo.jp,fesoku.net,fiveslot777.com,gamejksokuhou.com,girlsreport.net,girlsvip-matome.com,grasoku.com,gundamlog.com,honyaku-channel.net,ikarishintou.com,imas-cg.net,imihu.net,inutomo11.com,itainews.com,itaishinja.com,jin115.com,jisaka.com,jnews1.com,jumpsokuhou.com,jyoseisama.com,keyakizaka46matomemory.net,kidan-m.com,kijoden.com,kijolariat.net,kijolifehack.com,kijomatomelog.com,kijyokatu.com,kijyomatome.com,kijyomatome-ch.com,kijyomita.com,kirarafan.com,kitimama-matome.net,kitizawa.com,konoyubitomare.jp,kotaro269.com,kyousoku.net,ldblog.jp,livedoor.biz,livedoor.blog,majikichi.com,matacoco.com,matomeblade.com,matomelotte.com,matometemitatta.com,mojomojo-licarca.com,morikinoko.com,nandemo-uketori.com,netatama.net,news-buzz1.com,news30over.com,nmb48-mtm.com,norisoku.com,npb-news.com,ocsoku.com,okusama-kijyo.com,onihimechan.com,orusoku.com,otakomu.jp,otoko-honne.com,oumaga-times.com,outdoormatome.com,pachinkopachisro.com,paranormal-ch.com,recosoku.com,s2-log.com,saikyo-jump.com,shuraba-matome.com,ske48matome.net,squallchannel.com,sukattojapan.com,sumaburayasan.com,sutekinakijo.com,usi32.com,uwakich.com,uwakitaiken.com,vault76.info,vipnews.jp,vippers.jp,vipsister23.com,vtubernews.jp,watarukiti.com,world-fusigi.net,zakuzaku911.com,zch-vip.com##+js(set-local-storage-item, /_fa_Y2FjaGVfYWRibG9ja19jaXJjdW12ZW50X3Njb3Jl$/, $remove$)
meconomynews.com,brandbrief.co.kr,motorgraph.com,topstarnews.net##+js(noeval-if, /07c225f3\.online|content-loader\.com|css-load\.com|html-load\.com/)
||html-load.com^$domain=manta.com|tportal.hr|tvtropes.org|convertcase.net|zeta-ai.io
!#if cap_html_filtering
meconomynews.com,brandbrief.co.kr,motorgraph.com##^script:has-text(KCgpPT57bGV0IGU)
topstarnews.net,islamicfinder.org,secure-signup.net,dramabeans.com,dropgame.jp,manta.com,tportal.hr,tvtropes.org,convertcase.net##^script:has-text(error-report.com)
aikatu.jp,ark-unity.com,cool-style.com.tw,doanhnghiepvn.vn,mykhel.com,mynet.com##^script[onload*="error-report.com"]
!#else
meconomynews.com,brandbrief.co.kr,motorgraph.com##+js(rmnt, script, KCgpPT57bGV0IGU)
topstarnews.net,islamicfinder.org,secure-signup.net,dramabeans.com,dropgame.jp,manta.com,tportal.hr,tvtropes.org,convertcase.net##+js(rmnt, script, error-report.com)
||html-load.com^$redirect=noopjs,domain=aikatu.jp|ark-unity.com|cool-style.com.tw|doanhnghiepvn.vn|mynet.com
aikatu.jp,ark-unity.com,cool-style.com.tw,doanhnghiepvn.vn,mykhel.com,mynet.com##+js(nostif, error-report.com)
!#endif

! https://github.com/AdguardTeam/AdguardFilters/issues/91230
||nsfw.xxx/vendor/fingerprint/fingerprint2.min.js$script,redirect=fingerprint2.js,important

! https://www.reddit.com/r/uBlockOrigin/comments/p9lity/how_to_block_favicon_popups_on_these_websites/
||g.jwpsrv.com/g/gcid-*?notrack$frame

! https://github.com/uBlockOrigin/uAssets/issues/10012
tacobell.com##+js(set, bmak.js_post, false)

! https://github.com/easylist/easylist/pull/9136
||cloudflare.com/ajax/libs/fingerprintjs2/$script,redirect=fingerprint2.js,important,domain=gamebox.gesoten.com

! https://github.com/easylist/easylist/pull/9137
||gamerch.com/s3-assets/library/js/fingerprint2.min.js$script,redirect=fingerprint2.js,important

! https://github.com/AdguardTeam/AdguardFilters/issues/95660
||ahentai.top/counter.php
||caitlin.top/counter.php

! https://github.com/easylist/easylist/pull/9370
||tr.jianshu.com^

! https://github.com/easylist/easylist/pull/9469#issuecomment-950179366
/lib/f_ad_code.js

! https://github.com/Yuki2718/adblock/issues/40
! https://github.com/Yuki2718/adblock/issues/44
! https://www.reddit.com/r/uBlockOrigin/comments/udaxzt/block_fingerprinting_javascript_with_completely/i8xaru3/
/\.com\/[-_0-9a-zA-Z]{4,}\/[-\/_0-9a-zA-Z]{25,}$/$script,1p,domain=gu-global.com|uniqlo.com

! https://www.reddit.com/r/uBlockOrigin/comments/r06yju/sur_in_english_website_recognises_ad_blocker/
||metrics.surinenglish.com^

! https://github.com/uBlockOrigin/uAssets/issues/10615#issuecomment-980221624
@@||natureetdecouvertes.com^*/pixel.png$~third-party,badfilter

! https://github.com/uBlockOrigin/uAssets/issues/10630
||cm.bilibili.com/cm/api/$xhr

! https://github.com/uBlockOrigin/uAssets/issues/10679
||wannads.com/api/track/fingerprint^

! https://github.com/uBlockOrigin/uAssets/issues/10690
||wuzhuiso.com^$removeparam=src

! https://github.com/uBlockOrigin/uAssets/pull/10610
||va.huya.com^
||e-stat.huya.com^

! pornocolombiano.net analytics
||analytics.tiendaenoferta.com^

! https://github.com/uBlockOrigin/uAssets/issues/10995
||zhihu.com^$removeparam=hybrid_search_source
||zhihu.com^$removeparam=hybrid_search_extra

! https://github.com/easylist/easylist/issues/6724#issuecomment-1003172754
! https://github.com/uBlockOrigin/uAssets/pull/15692#issuecomment-1321098072
/cfga/jquery.js?$image

! https://github.com/uBlockOrigin/uAssets/issues/11278
||mynewsmedia.co/*/Linkpage/ads_stats_controller.php
||gplinks.co/Auth/ads_stats_controller.php

! https://github.com/uBlockOrigin/uAssets/issues/9970
||videovard.*/api/front/view^$xhr,important

! https://github.com/uBlockOrigin/uAssets/issues/11644
endbasic.dev,jmmv.dev##+js(no-xhr-if, method:POST)

! https://github.com/AdguardTeam/AdguardFilters/issues/106875
||b90.yahoo.co.jp^

! https://github.com/AdguardTeam/AdguardFilters/issues/110958
||jsdelivr.net^*/fp.min.js$script,redirect=fingerprint3.js:10

! https://github.com/uBlockOrigin/uAssets/issues/11885
/log/*$xhr,domain=vizcloud.*|vizcloud2.*

! https://github.com/uBlockOrigin/uAssets/issues/11895
||serasaexperian.com.br/dist/scripts/fingerprint2.js^$redirect=fingerprint2.js,script,important

! https://www.reddit.com/r/uBlockOrigin/comments/u13isu/how_to_block_fathom_tracking
/?p=%2F*&h=https%3A%2F%2F*&r=&sid=*&qs=*&cid=$image,1p
/?h=https%3A%2F%2F*&r=&sid=*&qs=*&cid=$image,1p
/?v=eyJoIjoiaHR0cHM6Ly9$image,1p
/?v=eyI*sImgiOiJodHRwczovL$image,1p
!/^https?:\/\/[-.0-9a-z]+\/script\.js$/$script,1p,strict3p,match-case

! https://assets.acdn.no/pkg/@amedia/browserid/1.1.6/index.js trackers
! https://github.com/uBlockOrigin/uAssets/pull/13408#issuecomment-1341756510
! ||no/api/aid/users/self?filter=*tracking$xhr

! https://github.com/uBlockOrigin/uAssets/issues/13958
||play.google.com/store/apps/*referrer$removeparam=referrer
||apps.apple.com/*/app/*referrer$removeparam=referrer

! https://github.com/uBlockOrigin/uAssets/issues/13970
||securemetrics.apple.com/b/ss/*maps$image,important

! https://github.com/uBlockOrigin/uAssets/issues/12889
||techpowerup.com/__botcheck$xhr
||techpowerup.com/js/mt

! https://github.com/uBlockOrigin/uAssets/issues/14653
||hktvmall.com/yuicombo?$script,removeparam=/_ui/shared/common/js/analytics/with-intersection-track.js
! https://github.com/uBlockOrigin/uAssets/issues/22702
! https://github.com/uBlockOrigin/uAssets/issues/22764
! ||hktvmall.com/yuicombo?$script,removeparam=/_ui/shared/common/js/InappCommunicationManager.js
! ||hktvmall.com/yuicombo?$script,removeparam=/_ui/shared/common/js/util/jquery.analytics-utils.js
! ||hktvmall.com/yuicombo?$script,removeparam=/^\/_ui\/desktop\/common\/js\/uiAnalytics\//
||hktvmall.com/_ui/desktop/common/js/uiAnalytics/
||hktvmall.com/_ui/shared/common/js/analytics/with-intersection-track.js
||hktvmall.com/_ui/shared/common/js/util/jquery.analytics-utils.js
||hktvmall.com/yuicombo|$script,1p

! https://github.com/uBlockOrigin/uAssets/issues/14850#issuecomment-1249571859
! https://github.com/uBlockOrigin/uAssets/issues/27336
/discourse-fingerprint-$domain=~btt.community

! https://github.com/easylist/easylist/issues/13695
ericdraken.com##+js(aopr, dataLayer)
ericdraken.com##^script[async]

! https://github.com/AdguardTeam/AdguardFilters/issues/81856
/s/s/js/m/om.js?v=

! https://github.com/uBlockOrigin/uAssets/issues/4059
! https://github.com/AdguardTeam/AdguardFilters/issues/135665
://vip.*/?pge=$image,3p
://ply.*/?v=$image,3p

! brave.com analytics
||brave.com/static-assets/js/analysis.js

! https://www.girlsofdesire.org/galleries/kana-kusakabe/00.html
/images/*/analytics.js$domain=girlsofdesire.org

! t3n.de tracking
||c2shb.pubgw.yahoo.com/admax/bid/partners/PBJS

! doucolle.net analytics
||blozoo.info/js/inouttool/

! https://github.com/uBlockOrigin/uAssets/issues/15809
||hikari.jiocinema.com/v1/batch^
||hikari.jiocinema.com/v1/track^

! https://github.com/uBlockOrigin/uAssets/issues/16478
!||linkedin.com/li/track$xhr,1p
! https://github.com/uBlockOrigin/uAssets/issues/22627
linkedin.com##+js(href-sanitizer, a[href^="https://www.linkedin.com/redir/redirect?url=http"], ?url)

! https://github.com/uBlockOrigin/uAssets/issues/16730#issuecomment-1427957300
utreon.com##+js(no-xhr-if, utreon.com/pl/api/event method:POST)

! https://github.com/uBlockOrigin/uAssets/issues/16731
/^https:\/\/[0-9a-z]{7,25}\.com\/v2(?:\/0\/)?(?=[-_0-9a-z]{0,84}[A-Z])(?=[-_a-zA-Z]{0,84}[0-9])[-_0-9a-zA-Z]{54,85}(#\?v=[0-9a-f]{32})?$/$script,xhr,3p,match-case
! https://github.com/uBlockOrigin/uBlock-discussions/discussions/461
! https://www.reddit.com/r/uBlockOrigin/comments/1ket4g1/adblock_detection_on_wwwrankercom/
/^https:\/\/[0-9a-z]{7,25}\.com\/(?:assets|build|bundles|chunks|dist|files|j|public|scripts|static)?\/?(?:js\/)?[0-9_a-z]{6,16}\/?[0-9_a-z]{5,120}(?:[-.](?:app|bundle|ma?in|module|prod|index|v\d|vendor))?(?:\.js)?$/$script,3p,match-case,to=~adatoolbar.com|~aswpsdkus.com|~chimpstatic.com|~clickiocmp.com|~m'''))
# TODO: Add real analysis here