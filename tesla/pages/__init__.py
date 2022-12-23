from tesla.pyhtml import PYHTML, CT
from tesla.pyhtml.tags import CSS


def ErrorPage(request, logs, title, heading1, heading2, debug):

    doc = PYHTML()
    head, body = doc.create_doc()
    # css
    style = CT('style', CSS('*', margin='0', boxSizing='border-box').css(),
               CSS('body', backgroundColor='floralwhite').css())
    h1_s = CSS('h1',
               backgroundColor='blue',
               padding='15px',
               color='white',
               borderBottom='10px solid black'

               )
    li_s = CSS('li',
               backgroundColor='lightblue',
               listStyle='none',
               padding='5px 10px',
               width='260px',
               margin='2px 0'
               )

    req_s = CSS('#req_body',
                borderTop='10px solid black',
                margin='10px 0'
                )
    style.append(h1_s.css(), li_s.css(), req_s.css())
    # head
    head.append(style, CT('title', title))

    # body
    h1 = CT('h1', title)
    p = CT('pre', CT('xmp', heading1),  style=CSS(
        margin='10px',
        marginLeft='40px',
        fontSize='x-large'
    ).css())

    ul = CT('ul')

    req_p = CT('p', 'Request body',  style=CSS(
         margin='10px',
         marginLeft='40px',
         fontSize='x-large'
         ).css())
    ul_req = CT('ul')
    req_b = CT('div', req_p, ul_req, id='req_body')
    for k, v in request.environ.items():
        x = CT('xmp', f'{k} = {v}')
        ul_req.append(CT('li', x, style=CSS(
            width='fit-content'
        ).css()))

    for l in logs:
        # print(route)
        x = CT('xmp', l)
        # if route.name:
        #     x.append(f'[name={route.name}]')
        ul.append(CT('li', x))

    if debug:
        body.append(h1, p, ul, req_b)
    else:
        body.append(title)
    return doc
    ...
