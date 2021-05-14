from app import create_app, db
from app.models import Channel, TestPoint, ChannelGroup, Job, Project, Customer
import math

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Channel': Channel, 'TestPoint': TestPoint, 'ChannelGroup': ChannelGroup,
            'Job': Job, 'Project': Project, 'Customer': Customer}

@app.context_processor
def utility_processor():
    return dict(round=round)

# TODO: inject in the ENG_UNITS into the context