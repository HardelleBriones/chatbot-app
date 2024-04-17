<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Block definition class for the block_pluginname plugin.
 *
 * @package   block_pluginname
 * @copyright Year, You Name <your@email.address>
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

class block_chatbot extends block_base {

    /**
     * Initialises the block.
     *
     * @return void
     */
    public function init() {
        $this->title = get_string('chatbot', 'block_chatbot');
    }

    /**
     * Gets the block contents.
     *
     * @return string The block HTML.
     */
    public function get_content() {
        global $OUTPUT;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new stdClass();
        $this->content->footer = '';

        // Path to the local HTML file
        $html_path = 'C:\Users\Lloyd\Documents\GitHub\Moodle\server\moodle\blocks\chatbot\chatbot_design\index.html';

        // Read HTML content from the file
        $html_content = file_get_contents($html_path);

        if ($html_content !== false) {
            $this->content->text = $html_content;
        } else {
            $this->content->text = 'Failed to load HTML content.';
        }

        // Enqueue CSS file
        $css_url = new moodle_url('/blocks/chatbot/chatbot_design/styles.css');
        $this->page->requires->css($css_url);

        // Enqueue JavaScript file
        $js_url = new moodle_url('/blocks/chatbot/chatbot_design/script.js');
        $this->page->requires->js($js_url);

        return $this->content;
    }

    /**
     * Defines in which pages this block can be added.
     *
     * @return array of the pages where the block can be added.
     */
    public function applicable_formats() {
        return [
            'admin' => false,
            'site-index' => true,
            'course-view' => true,
            'mod' => false,
            'my' => true,
        ];
    }
}