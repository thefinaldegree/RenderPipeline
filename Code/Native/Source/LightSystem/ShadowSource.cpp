#include "ShadowSource.h"


ShadowSource::ShadowSource() {
    _last_time_rendered = -1;
    _needs_update = true;
    _slot = -1;
    _transform = NULL;
    _resolution = 512;
    _region.set(-1, -1);
}

ShadowSource::~ShadowSource() {

}