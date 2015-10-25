import requests

# our html parser
from bs4 import BeautifulSoup


class Parser(object):
    """Parser : Reads the internet to get the tracklists"""
    # default website
    url = 'http://www.1001tracklists.com/'

    def __init__(self, url=None):
        super(Parser, self).__init__()
        if url:
            self.url = url

    def get_tracklist_html(self, path=None):
        '''Returns the tracklist's page html'''
        url = self.url + 'tracklist/'

        if not path:
            raise Exception('No url provided')
        else:
            url += path

        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
        else:
            raise Exception('Response error {}'.format(response.status_code))

        return html

    def parse_tracklist(self, html=None):
        '''Returns the parsed tracklist as a list of dict.
        each dict is a sound representation as follows:
        parsed_tracklist = [sound, sound, ...]
        sound = {
            artist:
            title:
            time:
            previous:
            next:
        }'''
        if not html:
            raise Exception('Parse Error: no html provided')
        soup_html5 = BeautifulSoup(html, 'html5lib')

        # GET GLOBAL INFOS
        tag = soup_html5.select('#middleDiv')[0].table.tr.td.div
        infos = self.get_infos(tag)

        # GET THE TRACKS
        # using different parsers because the document is definetly not well
        # formed, this is quite boring in term of memory use...
        tracks = list()
        soup_htmlparser = BeautifulSoup(html, 'html.parser')
        found_tracks = 0
        tag = soup_htmlparser.select('#middleDiv')[0].table.tr.td.div.table
        for tr in tag.contents:
            if tr.name == 'tr':
                for td in tr.contents:
                    if td.name == 'td':
                        for div in td.contents:
                            if div.name == 'div':
                                try:
                                    if div['itemprop'] == 'tracks':
                                        found_tracks += 1
                                        track = self.get_track(str(div))
                                        track['position'] = found_tracks
                                        tracks.append(track)
                                except:
                                    pass
        return [infos, tracks, found_tracks]

    def get_infos(self, tag):
        '''Gets the info tag and returns the info dict'''
        infos = dict()
        infos['genres'] = list()
        infos['authors'] = list()
        for item in tag.contents:
            if item.name == 'meta':
                if item['itemprop'] == 'name':
                    infos['name'] = item['content']
                if item['itemprop'] == 'datePublished':
                    infos['datePublished'] = item['content']
                if item['itemprop'] == 'numTracks':
                    infos['numTracks'] = item['content']
                if item['itemprop'] == 'genre':
                    infos['genres'].append(item['content'])
                if item['itemprop'] == 'author':
                    infos['authors'].append(item['content'])
        return infos

    def get_track(self, str_tag):
        '''Gets the track tag and returns the track dict'''
        track = dict()
        track_soup = BeautifulSoup(str_tag, 'html5lib')
        tag = track_soup.div
        for item in tag.contents:
            if item.name == 'meta':
                if item['itemprop'] == 'byArtist':
                    track['byArtist'] = item['content']
                if item['itemprop'] == 'name':
                    track['name'] = item['content']
                if item['itemprop'] == 'duration':
                    track['duration'] = item['content']
                if item['itemprop'] == 'publisher':
                    track['publisher'] = item['content']
                if item['itemprop'] == 'url':
                    track['url'] = item['content']
                    url = str(track['url'])
                    # parse id
                    identifier = ''
                    i = 7
                    while True:
                        if not url[i].isdigit():
                            break
                        identifier += url[i]
                        i += 1
                    if identifier == '':
                        identifier += '@'
                    track['identifier'] = identifier

        return track


def test():
    p = Parser()
    html = p.get_tracklist_html(
        '72910_four-tet-jamie-xx-bbc-radio-1-essential-mix-2015-03-28.html'
    )
    r = p.parse_tracklist(html)
    for key, value in r[0].items():
        print('{} => {}'.format(key, value))
        print('')
    for item in r[1]:
        for key, value in item.items():
            print('{} => {}'.format(key, value))
        print('')
    return r


# STRUCTURE

# <div class="middleDiv" id="middleDiv">
#     <table class="middle">
#         <tr>
#             <td>
#                 <div itemscope itemtype="http://schema.org/MusicPlaylist">
#                     <meta itemprop="name" content="<Title>">
#                     <meta itemprop="datePublished" content="<date>">
#                     <meta itemprop="numTracks" content="<track_number>">
#                     <meta itemprop="genre" content="<genreS>">
#                     <meta itemprop="author" content="<authorS>">
#                     <table class="default full tl hover">


# TRACK LINE

# <colgroup>
#     <col style="width:3em;">
#     <col style="width:1px;">
#     <col>
# </colgroup>
# <tr>
#     <th class="left">&nbsp;#</th>
#     <th></th>
#     <th class="left">Artist - Title (Remix)</th>
# </tr>
# <tr id="tlp_1350347" onclick="$A(document.getElementsByClassName('tlRowActive')).each(function(item) { item.removeClassName('tlRowActive'); }); this.addClassName('tlRowActive');" class=" topBorder tlpItem trRow1">
#     <td id="tlp0_number_column" class="left">
#         <input type="hidden" id="tlp_tracknumber_0" value="1"> <span id="tlp0_tracknumber" class="tlFontLarge"> <span id="tlp0_tracknumber_value">01</span> </span> <span id="cue_1350347" class="cueValueField">02:15</span> <input id="tlp_cue_seconds_1350347" type="hidden" value="135">
#         <div class="tlEdit"> <input id="tlp0_cue_string" type="text" size="4" maxlength="6" class="" placeholder="cue" value="02:15" title="cue as minutes only or minutes:seconds" onchange="checkCueValue(this, { idInput: 'tlp0', idPos: '1350347' } );" onfocus="activateFormField(this);"> </div>
#     </td>
#     <td id="tlp0_playcolumn">
#         <div id="tlp_play_col_1350347"> </div>
#     </td>
#     <td class="" id="tlptr_1350347">
#         <div id="tlp_0"></div>
#         <div itemprop="tracks" itemscope itemtype="http://schema.org/MusicRecording">
#             <meta itemprop="byArtist" content="Jamie XX">
#             <meta itemprop="name" content="Gosh">
#             <meta itemprop="duration" content="PT4M51S">
#             <meta itemprop="publisher" content="YOUNG TURKS">
#             <meta itemprop="url" content="/track/246355_jamie-xx-gosh/index.html">
#             <div id="tlptrrow_0">
#                 <div class="floatL" id="tlptrv_0" >
#                     <div id="tlp0_content" class="inlineBlock">
#                         <div id="tr_246355" class="inlineBlock tlFont trackValue">
#                             <div id="tr_246355" class="trackFormat inlineBlock"><a href="/track/246355_jamie-xx-gosh/index.html" class="">Jamie XX - Gosh</a>&thinsp;</div>
#                             <div class="trackLabel inlineBlock" id="tlp0_labeldata">[<a href="/label/3328_young-turks/index.html" class="" title="Young Turks">YOUNG TURKS</a>]</div>
#                         </div>
#                     </div>
#                     <div class="clearL"></div>
#                     <div id="tlp0_idercolumn" class="tlIder halfOpacityOver" title="IDer of this track">
#                         <div class="sprite sprite-tick floatL mAlign infoImgDiv"></div>
#                         <div class="floatL"> <a href="/user/oxygen15/index.html" target="_blank">oxygen15</a> (18.4k) </div>
#                     </div>
#                 </div>
#             </div>
#             <div id="tlp0_media_buttons" class="floatL">
#                 <div class="s32 s32-video actionIcon floatL" id="play_vid_1350347" title="show video player" onclick="new MediaViewer(this, 'tlptr_1350347', { idObject: '5', idItem: '246355', idMediaType: '2', viewSource: 1, viewItem: 72910 } );">
#                     <div class="s32 s32-play_overlay"></div>
#                 </div>
#                 <div class="s32 s32-beatport actionIcon floatL" id="play_bp_1350347" title="show beatport player" onclick="new MediaViewer(this, 'tlptr_1350347', { idObject: '5', idItem: '246355', idSource: '1', viewSource: 1, viewItem: 72910 } );">
#                     <div class="s32 s32-play_overlay"></div>
#                 </div>
#             </div>
#             <a href="http://www.google.com/search?q=Jamie+XX+Gosh" target="_blank" style="white-space: nowrap;" class="inlineBlock mAlign floatL actionHover" title="search the web">
#                 <div class=" s32 s32-search "></div>
#             </a>
#         </div>
#         <div id="tlp0_actions" class="clearL tlHover" style="padding-top:5px;">
#             <div class="s32 s32-video actionHover floatL noUser interaction" id="add_video_246355" title="add a video for this track" onclick="new MediaSubmitter(this, 'add_video', 'track', { idObject: '5', idItem: '246355' } );">
#                 <div class="s32 s32-add_overlay"></div>
#             </div>
#             <div class="s32 s32-soundcloud actionHover floatL noUser interaction" title="add a soundcloud link" id="add_audio_1350347" onclick="new MediaSubmitter(this, 'add_media', 'soundcloud', { idObject: '5', idItem: '246355' } );">
#                 <div class="s32 s32-add_overlay"></div>
#             </div>
#             <div class="s32 s32-beatport actionHover floatL noUser interaction" title="add a beatport link" id="add_bp_1350347" onclick="new MediaSubmitter(this, 'add_media', 'beatport', { idObject: '5', idItem: '246355' } );">
#                 <div class="s32 s32-add_overlay"></div>
#             </div>
#             <div class="s32 s32-add actionHover floatL noUser interaction" title="add another track (suggestion)" id="add_sug_1350347" onclick="new UserSuggest(this, { type: 'add', idTL: '72910' , idTLP: '1350347', isID: true, hasCue: 1, trackNo: '1' ,isLive: 0 } ).show();"></div>
#             <div class="s32 s32-error actionHover floatL noUser interaction" title="report a track(list) fault / correction" id="add_sug_cor_1350347" onclick="new UserSuggest(this, { type: 'wrong', idTL: '72910', idTLP: '1350347' ,isID: false, hasCue: 1, trackNo: '1' , isLinked: 0 ,isLive: 0 , hasLabel: true, isBootleg: 0 } ).show();">
#                 <div class="s32 s32-add_overlay"></div>
#             </div>
#         </div>
#         <div class="tlHover">
#             <div id="tlp0_editactions" class="tlEdit floatR">
#                 <div class="s32 s32-edit actionHover floatL" title="edit this position" onclick="submitForm(this, { pos: 0, vpos: '', action: 'btn_edit'})" ></div>
#                 <div class="s32 s32-add actionHover floatL" title="insert a new position here" onclick="submitForm(this, { pos: 0, vpos: '', action: 'btn_insert' })"></div>
#                 <div class="s32 s32-add actionHover floatL" title="insert an ID track position here (without edit)" onclick="submitForm(this, { pos: 0, action: 'btn_insert_id', anker: 'tlp_0' })">
#                     <div class="s32 s32-id_overlay"></div>
#                 </div>
#                 <div title="delete this position" onclick="submitForm(this, { pos: 0, vpos: '', tlp0_delete: true, anker: 'tlp_1350347' })" class="s32 s32-trash actionHover floatL"></div>
#                 <div class="s32 s32-arrow_up_small floatL noPointer halfOpacity" title="move up this position" onclick="submitForm(this, { pos: 0, vpos: '', action: 'btn_moveup', anker: 'tlp_1350347' })"></div>
#                 <input type="text" value="" id="tlp0_action_count" class="topAlign floatL tlEditInput" onfocus="activateFormField(this);" title="numeric value to move entry x positions">
#                 <div class="s32 s32-arrow_down_small floatL actionHover" onclick="submitForm(this, { pos: 0, vpos: '', action: 'btn_movedown', anker: 'tlp_1350347' })" title="move down this position"></div>
#                 <div class="clearR"></div>
#             </div>
#         </div>
#         <div class="clearL"></div>
#         <div class="clearR"></div>
#     </td>
# </tr>

